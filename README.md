# hypersync-client-python

[![PyPI](https://img.shields.io/pypi/v/hypersync)](https://pypi.org/project/hypersync/) [![Python Versions](https://img.shields.io/pypi/pyversions/hypersync)](https://pypi.org/project/hypersync/) [![Discord](https://img.shields.io/badge/Discord-Join%20Chat-7289da?logo=discord&logoColor=white)](https://discord.com/invite/envio)

Python client for [Envio's](https://envio.dev) HyperSync. Built on top of the Rust implementation via PyO3 bindings, providing high-performance blockchain data access with a Pythonic interface.

## What is HyperSync?

[HyperSync](https://docs.envio.dev/docs/HyperSync/overview) is Envio's high-performance blockchain data retrieval layer. It is a purpose-built alternative to JSON-RPC endpoints, offering up to 2000x faster data access across 70+ EVM-compatible networks and Fuel.

HyperSync lets you query logs, transactions, blocks, and traces with flexible filtering and field selection, returning only the data you need.

## Features

- **High performance**: Built on a Rust core for maximum efficiency
- **Pythonic interface**: Full type hints and async/await support
- **Multiple output formats**: JSON, Parquet, and CSV export
- **Flexible queries**: Filter logs, transactions, blocks, and traces
- **Field selection**: Retrieve only the fields you need
- **Preset queries**: Built-in helpers for common query patterns
- **Streaming**: Process large datasets without loading everything into memory
- **70+ networks**: Access any [HyperSync-supported network](https://docs.envio.dev/docs/HyperSync/hypersync-supported-networks)

## Installation

```bash
pip install hypersync
```

Requires Python 3.9 or newer.

## API Token

An API token is required to use HyperSync. [Get your token here](https://docs.envio.dev/docs/HyperSync/api-tokens), then set it as an environment variable:

```bash
export ENVIO_API_TOKEN="your-token-here"
```

## Quick Start

Fetch all Transfer event logs from a USDT contract on Ethereum:

```python
import os
import asyncio
import hypersync

async def main():
    client = hypersync.HypersyncClient(hypersync.ClientConfig(
        url="https://eth.hypersync.xyz",
        bearer_token=os.environ["ENVIO_API_TOKEN"]
    ))

    usdt_contract = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

    # ERC-20 Transfer event topic0
    transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

    query = hypersync.preset_query_logs_of_event(
        usdt_contract,
        transfer_topic,
        from_block=17_000_000,
        to_block=17_000_100
    )

    res = await client.get(query)
    print(f"Found {len(res.data.logs)} Transfer events")

asyncio.run(main())
```

See the [examples directory](./examples) for more patterns including block data, wallet transactions, Uniswap swap events, Parquet export, and streaming with a progress bar.

## Connecting to Different Networks

Change the `url` to connect to any supported network:

```python
# Arbitrum
client = hypersync.HypersyncClient(hypersync.ClientConfig(
    url="https://arbitrum.hypersync.xyz",
    bearer_token=os.environ["ENVIO_API_TOKEN"]
))

# Base
client = hypersync.HypersyncClient(hypersync.ClientConfig(
    url="https://base.hypersync.xyz",
    bearer_token=os.environ["ENVIO_API_TOKEN"]
))
```

See the full list of [supported networks and URLs](https://docs.envio.dev/docs/HyperSync/hypersync-supported-networks).

## Running Examples

```bash
# Recommended: use a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with example dependencies
pip install -e ".[examples]"

# Set your API token
export ENVIO_API_TOKEN="your-token-here"

# Run an example
python examples/simple_logs_of_event.py
```

## Documentation

- [HyperSync Documentation](https://docs.envio.dev/docs/HyperSync/overview)
- [Query Reference](https://docs.envio.dev/docs/HyperSync/hypersync-query)
- [All Client Libraries](https://docs.envio.dev/docs/HyperSync/hypersync-clients) (Node.js, Rust, Go)
- [PyPI Package](https://pypi.org/project/hypersync/)

## FAQ

**How does this compare to using JSON-RPC or web3.py?**
HyperSync retrieves data up to 2000x faster than traditional JSON-RPC. Scanning all ERC-20 transfers on Ethereum mainnet takes seconds rather than hours.

**Do I need an API token?**
Yes, an API token is required. [Get one here](https://docs.envio.dev/docs/HyperSync/api-tokens).

**Which networks are supported?**
70+ EVM-compatible networks and Fuel. See the [full list](https://docs.envio.dev/docs/HyperSync/hypersync-supported-networks).

**Can I export data to Parquet or CSV?**
Yes. The client supports Parquet and CSV output formats. See `examples/parquet_blocks_and_transactions.py` for an example.

**Is this suitable for data science workflows?**
Yes. The Python client is a good fit for data analytics, research, and workflows that integrate with pandas, numpy, or other Python data tools.

**How is this different from the Rust client?**
This client is built on top of the [Rust client](https://github.com/enviodev/hypersync-client-rust) via PyO3 bindings. It provides a Pythonic interface with full type hints. The Rust client offers the lowest-level access with the least overhead.

## Support

- [Discord community](https://discord.com/invite/envio)
- [GitHub Issues](https://github.com/enviodev/hypersync-client-python/issues)
- [Documentation](https://docs.envio.dev/docs/HyperSync/overview)
