import hypersync
import asyncio
import time
from hypersync import LogField

DAI_ADDRESS = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

async def main():
    # Create hypersync client using the mainnet hypersync endpoint (default)
    client = hypersync.HypersyncClient(hypersync.ClientConfig())

    height = await client.get_height()

    # The query to run
    query = hypersync.Query(
        # start from tip and get only new events
        from_block=height,
		# Select all logs from dai contract address
        logs=[hypersync.LogSelection(
			address=[DAI_ADDRESS],
			topics=[["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]],
		)],
        # Select the fields we want, we get all fields we need for decoding the logs
        field_selection=hypersync.FieldSelection(
			log=[
				LogField.DATA,
				LogField.ADDRESS,
				LogField.TOPIC0,
				LogField.TOPIC1,
				LogField.TOPIC2,
				LogField.TOPIC3,
			]
		)
    )

    decoder = hypersync.Decoder([
        "Transfer(address indexed from, address indexed to, uint256 value)"
    ])

    total_dai_volume = 0
    while True:
        res = await client.get(query)

        if len(res.data.logs) > 0:
            # Decode the log on a background thread so we don't block the event loop.
            # Can also use decoder.decode_logs_sync if it is more convenient.
            decoded_logs = await decoder.decode_logs(res.data.logs)

            for log in decoded_logs:
                #skip invalid logs
                if log is None:
                    continue

                total_dai_volume += log.body[0].val
        
        print(f"total DAI transfer volume is {total_dai_volume / 1e18} USD")

        height = res.archive_height
        while height < res.next_block:
            print(f"waiting for chain to advance. Height is {height}")
            height = await client.get_height()
            time.sleep(1)

        # continue query from next_block
        query.from_block = res.next_block

asyncio.run(main())
