import hypersync
import asyncio

# The address we want to get all ERC20 transfers and transactions for
ADDR = "1e037f97d730Cc881e77F01E409D828b0bb14de0"

# The query to run
QUERY = {
    # start from block 0 and go to the end of the chain (we don't specify a toBlock).   
    "from_block": 0,
    # The logs we want. We will also automatically get transactions and blocks relating to these logs (the query implicitly joins them)
    "logs": [
        {
            "topics": [
                # We want ERC20 transfers
                ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
                [],
                # We want the transfers that go to this address.
                # appending zeroes because topic is 32 bytes but address is 20 bytes
                ["0x000000000000000000000000" + ADDR],
            ],
        },
        {
            "topics": [
                # We want ERC20 transfers
                ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
                # We want the transfers that go to this address.
                # appending zeroes because topic is 32 bytes but address is 20 bytes
                ["0x000000000000000000000000" + ADDR],
                [],
            ],
        },
    ],
    "transactions": [
        # We want all the transactions that come from this address
        {"from": ["0x" + ADDR]},
        # We want all the transactions that went to this address
        {"to": ["0x" + ADDR]},
    ],
    # Select the fields we are interested in
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


async def test_query_parquet():
    client = hypersync.hypersync_client(
        "https://eth.hypersync.xyz",
    )
    await client.create_parquet_folder(QUERY, "data")
    print("test_query_parquet passed")


async def test_send_req():
    client = hypersync.hypersync_client(
        "https://eth.hypersync.xyz",
    )
    res = await client.send_req(QUERY)
    # print(res.data.logs)
    print("test_send_req passed")


async def test_get_height():
    client = hypersync.hypersync_client(
        "https://eth.hypersync.xyz",
    )
    height = await client.get_height()
    print("test_get_height passed")


async def test_decode_logs():
    client = hypersync.hypersync_client(
        "https://eth.hypersync.xyz",
    )
    res = await client.send_req(QUERY)
    with open('./erc20.abi.json', 'r') as json_file:
        json = json_file.read()
    abis = {}
    for log in res.data.logs:
        abis[log.address] = json
    decoder = hypersync.Decoder(abis)
    decoded_logs = decoder.decode_logs_sync(res.data.logs)
    for decoded_log in decoded_logs:
        print(decoded_log.indexed)
        print(decoded_log.body)
    print("test_decode_logs passed")


async def test_decode_events():
    client = hypersync.hypersync_client(
        "https://eth.hypersync.xyz",
    )
    res = await client.send_events_req(QUERY)
    with open('./erc20.abi.json', 'r') as json_file:
        json = json_file.read()
    abis = {}
    for event in res.events:
        abis[event.log.address] = json
    decoder = hypersync.Decoder(abis)
    decoded_events = decoder.decode_events_sync(res.events)
    for decoded_event in decoded_events:
        print(decoded_event.indexed)
        print(decoded_event.body)
    
    print("test_decode_events passed")


async def main():
    await test_decode_logs()
    await test_decode_events()
    await test_query_parquet()
    await test_send_req()
    await test_get_height()

asyncio.run(main())


