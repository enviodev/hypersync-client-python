import hypersync
import asyncio

# returns all logs of a the swap event from the uniswap v2 eth/rai swap pool within a block range

async def main():
    # Create hypersync client using the ethereum mainnet hypersync endpoint (default)
    client = hypersync.HypersyncClient(hypersync.ClientConfig())

    eth_rai_swap_pool = "0x3e47D7B7867BAbB558B163F92fBE352161ACcb49"

    # topic0 of swap event signature (hash of event signature)
    # query will return logs of this event
    # Swap(address indexed sender, uint256 amount0In, uint256 amount1In, uint256 amount0Out, uint256 amount1Out, address indexed to)
    event_topic_0 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"

    start_block = 0 
    end_block = 20_333_826

    query = hypersync.preset_query_logs_of_event(eth_rai_swap_pool, event_topic_0, start_block, end_block)

    print("Running the query...")

    # Run the query once, the query is automatically paginated so it will return when it reaches some limit (time, response size etc.)
    # there is a next_block field on the response object so we can set the from_block of our query to this value and continue our query until
    # res.next_block is equal to res.archive_height or query.to_block in case we specified an end block.
    res = await client.get(query)

    print(f"Query returned {len(res.data.logs)} logs of transfer events from contract {eth_rai_swap_pool}")



asyncio.run(main())
