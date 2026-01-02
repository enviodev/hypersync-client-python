import os
from dotenv import load_dotenv
import hypersync
import asyncio

# Load environment variables from a .env file
load_dotenv()

async def main():
    client = hypersync.HypersyncClient(hypersync.ClientConfig(
        url="https://eth.hypersync.xyz/",
        bearer_token=os.getenv("ENVIO_API_TOKEN")
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
