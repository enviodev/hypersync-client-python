import os
import hypersync
import asyncio
from hypersync import BlockField, TransactionField, LogField, ClientConfig


async def main():
    cfg = ClientConfig(bearer_token=os.environ.get("ENVIO_API_TOKEN"))
    client = hypersync.HypersyncClient(cfg)

    chain_id = await client.get_chain_id()

    print(chain_id)


asyncio.run(main())
