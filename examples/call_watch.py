import hypersync
import asyncio
import time
from hypersync import TransactionField

DAI_ADDRESS = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

async def main():
    # Create hypersync client using the mainnet hypersync endpoint (default)
    client = hypersync.HypersyncClient(hypersync.ClientConfig())

    # The query to run
    query = hypersync.Query(
        # start from tip and get only new events
        from_block=20519993,
		# Select all logs from dai contract address
        transactions=[hypersync.TransactionSelection(from_=[DAI_ADDRESS]), hypersync.TransactionSelection(to=[DAI_ADDRESS])],
        # Select the fields we want, we get all fields we need for decoding the logs
        field_selection=hypersync.FieldSelection(
			transaction=[
				TransactionField.HASH,
                TransactionField.INPUT,
			]
		)
    )

    decoder = hypersync.CallDecoder([
        "transfer(address dst, uint256 wad)"
    ])

    while True:
        res = await client.get(query)

        if len(res.data.transactions) > 0:
            # Decode the log on a background thread so we don't block the event loop.
            # Can also use decoder.decode_logs_sync if it is more convenient.
            decoded_calls = await decoder.decode_transactions_input(res.data.transactions)
            for call in decoded_calls:
                if call:
                    print(f"Call decoded: addr: {call[0].val}, wad: {call[1].val}")

        height = res.archive_height
        while height < res.next_block:
            print(f"waiting for chain to advance. Height is {height}")
            height = await client.get_height()
            time.sleep(1)

        # continue query from next_block
        query.from_block = res.next_block

asyncio.run(main())
