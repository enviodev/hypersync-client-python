import hypersync_client
import asyncio

async def main():

    client = hypersync_client.HypersyncClient(
        "https://eth.hypersync.xyz",
    )

    height = await client.get_height()

    print("Height:", height)

    addr = "1e037f97d730Cc881e77F01E409D828b0bb14de0"

    query = {
        "from_block": 0,
        "logs": [
            {
                "topics": [
                    ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
                    [],
                    ["0x000000000000000000000000" + addr],
                ],
            },
            {
                "topics": [
                    ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
                    ["0x000000000000000000000000" + addr],
                    [],
                ],
            },
        ],
        "transactions": [
            {"from": ["0x" + addr]},
            {"to": ["0x" + addr]},
        ],
        "field_selection": {
            "block": ["number", "timestamp", "hash"],
            "log": [
                "block_number",
                "log_index",
                "transaction_index",
                "data",
                "address",
                "topic0",
                "topic1",
                "topic2",
                "topic3",
            ],
            "transaction": [
                "block_number",
                "transaction_index",
                "hash",
                "from",
                "to",
                "value",
                "input",
            ],
        },
    }

    print(query)

    # res = await client.send_req(query)
    # print(res)
     
    await client.create_parquet_folder(query, "data")
    print("finished writing parquet folder")


asyncio.run(main())