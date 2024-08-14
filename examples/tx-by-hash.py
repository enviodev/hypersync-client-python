import hypersync
import asyncio
from hypersync import (
    JoinMode,
    TransactionField,
    ClientConfig,
    TransactionSelection,
)


async def main():
    client = hypersync.HypersyncClient(ClientConfig())

    # The query to run
    query = hypersync.Query(
        from_block=0,
        join_mode=JoinMode.JOIN_NOTHING,
        field_selection=hypersync.FieldSelection(
            transaction=[
                TransactionField.BLOCK_NUMBER,
                TransactionField.TRANSACTION_INDEX,
                TransactionField.HASH,
                TransactionField.FROM,
                TransactionField.TO,
                TransactionField.VALUE,
                TransactionField.INPUT,
            ]
        ),
        transactions=[
            TransactionSelection(
                hash=[
                    "0x410eec15e380c6f23c2294ad714487b2300dd88a7eaa051835e0da07f16fc282"
                ]
            )
        ],
    )

    print("Running the query...")

    # Run the query once, the query is automatically paginated so it will return when it reaches some limit (time, response size etc.)
    # there is a next_block field on the response object so we can set the from_block of our query to this value and continue our query until
    # res.next_block is equal to res.archive_height or query.to_block in case we specified an end block.
    res = await client.get(query)

    print(f"Ran the query once.  Next block to query is {res.next_block}")

    print(res.data.transactions[0].from_)
    print(res.data.transactions[0].to)


asyncio.run(main())
