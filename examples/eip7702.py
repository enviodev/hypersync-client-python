## NOTE : not all hypersync sources have this data, if no data returned and you're expecting it to - please let the team know in discord.

import hypersync
import asyncio
from hypersync import BlockField, JoinMode, TransactionField, LogField, ClientConfig

async def main():
    client = hypersync.HypersyncClient(ClientConfig())

    # The query to run
    query = hypersync.Query(
        # only get block 20224332
        from_block=22490287,
        to_block=22490287,
        include_all_blocks=True,
        join_mode=JoinMode.JOIN_ALL,
        field_selection=hypersync.FieldSelection(
            block=[BlockField.NUMBER, BlockField.TIMESTAMP, BlockField.HASH],
            transaction=[
                TransactionField.HASH,
                TransactionField.AUTHORIZATION_LIST,
			]
		),

    )

    print("Running the query...")

    # Run the query once, the query is automatically paginated so it will return when it reaches some limit (time, response size etc.)
    # there is a next_block field on the response object so we can set the from_block of our query to this value and continue our query until
    # res.next_block is equal to res.archive_height or query.to_block in case we specified an end block.
    res = await client.get(query)

    print(f"Ran the query once.  Next block to query is {res.next_block}")

    print(len(res.data.blocks))
    print(len(res.data.transactions))

    for transaction in res.data.transactions:
        print(transaction.authorization_list)

    print(len(res.data.logs))

asyncio.run(main())
