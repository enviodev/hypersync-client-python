# hypersync-client-python
Python package for [Envio's](https://envio.dev/) HyperSync client written in Rust

feedback and issues are appreciated :)


### Can find more examples in `examples/`

Ex: run `examples/all-erc20.py`

`$ python3 examples/all-erc20.py`

### Example usage
```python
import hypersync
import asyncio

async def main():

    # Create hypersync client using the mainnet hypersync endpoint
    client = hypersync.hypersync_client(
        "https://eth.hypersync.xyz",
    )

    height = await client.get_height()
    print("Height:", height)

    # The address we want to get all ERC20 transfers and transactions for
    addr = "1e037f97d730Cc881e77F01E409D828b0bb14de0"

    # The query to run
    query = {
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
                    ["0x000000000000000000000000" + addr],
                ],
            },
            {
                "topics": [
                    # We want ERC20 transfers
                    ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
                    # We want the transfers that go to this address.
                    # appending zeroes because topic is 32 bytes but address is 20 bytes
                    ["0x000000000000000000000000" + addr],
                    [],
                ],
            },
        ],
        "transactions": [
            # We want all the transactions that come from this address
            {"from": ["0x" + addr]},
            # We want all the transactions that went to this address
            {"to": ["0x" + addr]},
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

    print("query: ", query)

    # run the query once
    res = await client.send_req(query)
    print("res: ", res)

    # read json abi file for erc20
    with open('./erc20.abi.json', 'r') as json_file:
        abi = json_file.read()

    # every log we get should be decodable by this abi but we don't know
    # the specific contract addresses since we are indexing all erc20 transfers.
    abis = {}
    for log in res.data.logs:
        abis[log.address] = abi

    # create a decoder based on our abi file
    decoder = hypersync.Decoder(abis)
    
    # decode the logs using the decoder
    decoded_logs = decoder.decode_logs_sync(res.data.logs)

    print("decoded logs:")
    for decoded_log in decoded_logs:
        print(decoded_log.indexed)
        print(decoded_log.body)

    # Create a parquet folder by running this query and writing the contents to disk
    await client.create_parquet_folder(query, "data")
    print("finished writing parquet folder")


asyncio.run(main())
```