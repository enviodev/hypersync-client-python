import os
from dotenv import load_dotenv
import hypersync
import asyncio

# Load environment variables from a .env file
load_dotenv()

# returns all blocks and the hashes of the transactions (not entire transaction objects) within a block range

async def main():
    bearer_token = os.getenv("ENVIO_API_TOKEN")
    if not bearer_token:
        raise ValueError("ENVIO_API_TOKEN environment variable is required. Please set it in your .env file.")

    client = hypersync.HypersyncClient(hypersync.ClientConfig(
        url="https://eth.hypersync.xyz/",
        bearer_token=bearer_token
    ))

    query = hypersync.preset_query_blocks_and_transaction_hashes(17_000_000, 17_000_050)

    print("Running the query...")

    # Run the query once, the query is automatically paginated so it will return when it reaches some limit (time, response size etc.)
    # there is a next_block field on the response object so we can set the from_block of our query to this value and continue our query until
    # res.next_block is equal to res.archive_height or query.to_block in case we specified an end block.
    res = await client.get(query)

    print(f"Query returned {len(res.data.blocks)} blocks and {len(res.data.transactions)} transaction hashes")



asyncio.run(main())
