import hypersync
import asyncio
import time

DAI_ADDRESS = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

async def main():
    # Create hypersync client using the mainnet hypersync endpoint
    client = hypersync.hypersync_client(
        "https://eth.hypersync.xyz",
    )

    # The query to run
    query = {
        # start from block 0 and go to the end of the chain (we don't specify a toBlock).
        "from_block": 0,
        "logs": [
          {
            "address": [DAI_ADDRESS],
            # We want the transfers
            "topics": [
              ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
              [],
              [],
              [],
            ]
          }
        ],
        # Select the fields we are interested in, notice topics are selected as topic0,1,2,3
        "field_selection": {
          "log": [
            "data",
            "address",
            "topic0",
            "topic1",
            "topic2",
            "topic3"
          ]
        },
    }

    # read json abi file for erc20
    with open('./erc20.abi.json', 'r') as json_file:
        abi = json_file.read()

    # Map of contract address -> abi
    abis = {
        DAI_ADDRESS: abi
    }

    # Create a decoder with out mapping
    decoder = hypersync.Decoder(abis)

    total_dai_volume = 0
    while True:
        res = await client.send_req(query)

        if len(res.data.logs) > 0:
            # Decode the log on a background thread so we don't block the event loop.
            # Can also use decoder.decode_logs_sync if it is more convenient.
            decoded_logs = await decoder.decode_logs(res.data.logs)

            for log in decoded_logs:
                total_dai_volume += log.body[0]
        
        print(f"scanned up to {res.next_block} and total DAI transfer volume is {total_dai_volume / 1e18} USD")

        if res.archive_height == res.next_block:
            # wait if we are at the head
            time.sleep(1)
            
        # continue query from next_block
        query['from_block'] = res.next_block
        

asyncio.run(main())
