import hypersync
import asyncio

# returns all blocks and the hashes of the transactions (not entire transaction objects) within a block range

async def main():
    # Create hypersync client using the mainnet hypersync endpoint (default)
    client = hypersync.HypersyncClient(hypersync.ClientConfig())

    query = hypersync.preset_query_blocks_and_transaction_hashes(17_000_000, 17_000_050)

    print("Running the query...")

    # Run the query once, the query is automatically paginated so it will return when it reaches some limit (time, response size etc.)
    # there is a next_block field on the response object so we can set the from_block of our query to this value and continue our query until
    # res.next_block is equal to res.archive_height or query.to_block in case we specified an end block.
    res = await client.get(query)

    print(f"Query returned {len(res.data.blocks)} blocks and {len(res.data.transactions)} transaction hashes")



asyncio.run(main())
