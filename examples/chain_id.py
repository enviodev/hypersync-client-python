import os
from dotenv import load_dotenv
import hypersync
import asyncio
from hypersync import BlockField, TransactionField, LogField, ClientConfig

# Load environment variables from a .env file
load_dotenv()

async def main():
    client = hypersync.HypersyncClient(ClientConfig(
        url="https://eth.hypersync.xyz/",
        bearer_token=os.getenv("ENVIO_API_TOKEN")
    ))

    chain_id = await client.get_chain_id()

    print(chain_id)


asyncio.run(main())
