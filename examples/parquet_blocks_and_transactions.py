import os
from dotenv import load_dotenv
import hypersync
import asyncio

# Load environment variables from a .env file
load_dotenv()

async def main():
    bearer_token = os.getenv("ENVIO_API_TOKEN")
    if not bearer_token:
        raise ValueError("ENVIO_API_TOKEN environment variable is required. Please set it in your .env file.")
    
    client = hypersync.HypersyncClient(hypersync.ClientConfig(
        url="https://eth.hypersync.xyz/",
        bearer_token=bearer_token
    ))
    height = await client.get_height()

    query = hypersync.preset_query_blocks_and_transactions(
        height - 8000, height)

    print("Starting parquet collection...")
    # Collect data to parquet file
    await client.collect_parquet(
        query=query,
        path="data",
        config=hypersync.StreamConfig()
    )

    print("\nParquet collection completed!")
    print("Data saved!")

if __name__ == "__main__":
    asyncio.run(main())
