import hypersync
import asyncio
from hypersync import BlockField, TransactionField, LogField, ClientConfig


async def main():
    client = hypersync.HypersyncClient(ClientConfig())

    chain_id = await client.get_chain_id()

    print(chain_id)


asyncio.run(main())
