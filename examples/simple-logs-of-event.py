import hypersync
import asyncio

# returns all logs of a specific event from a contract within a block range

async def main():
    # Create hypersync client using the mainnet hypersync endpoint (default)
    client = hypersync.HypersyncClient(hypersync.ClientConfig())

    usdt_contract = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

    # topic0 of transaction event signature (hash of event signature)
    # query will return logs of this event
    event_topic_0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

    query = hypersync.preset_query_logs_of_event(usdt_contract, event_topic_0, 17_000_000, 17_000_050)

    print("Running the query...")

    # Run the query once, the query is automatically paginated so it will return when it reaches some limit (time, response size etc.)
    # there is a next_block field on the response object so we can set the from_block of our query to this value and continue our query until
    # res.next_block is equal to res.archive_height or query.to_block in case we specified an end block.
    res = await client.get(query)

    print(f"Query returned {len(res.data.logs)} logs of transfer events from contract {usdt_contract}")



asyncio.run(main())
