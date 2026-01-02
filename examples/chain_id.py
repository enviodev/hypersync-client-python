import os
from dotenv import load_dotenv
import hypersync
import asyncio
from hypersync import BlockField, TransactionField, LogField, ClientConfig

# Load environment variables from a .env file
load_dotenv()

async def main():
    bearer_token = os.getenv("ENVIO_API_TOKEN")
    if not bearer_token:
        raise ValueError("ENVIO_API_TOKEN environment variable is required. Please set it in your .env file.")
    
    client = hypersync.HypersyncClient(ClientConfig(
        url="https://eth.hypersync.xyz/",
        bearer_token=bearer_token
    ))

    chain_id = await client.get_chain_id()

    print(chain_id)


asyncio.run(main())
