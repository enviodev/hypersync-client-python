# hypersync-client-python
Python package for [Envio's](https://envio.dev/) HyperSync client written in Rust

### Example usage
```python

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

```


To run locally
```
$ pyenv activate pyo3
$ maturin develop
$ python3
>>> import hypersync_client
>>> hypersync_client.send_req()
```

To publish to test PyPI
```
$ maturin publish -r testpypi
```

username: `__token__`

password: `<YOUR-TOKEN>`

make sure to include the `pypi-` prefix on your token and that your token doesn't contain any newline chars

using the deployed package:
    
    $ python -m pip install --index-url https://test.pypi.org/simple/ --no-deps hypersync

    $ python
    >>> import hypersync_client