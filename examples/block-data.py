import hypersync
import asyncio
from hypersync import BlockField, JoinMode, TransactionField, LogField, ClientConfig

async def main():
    client = hypersync.HypersyncClient(ClientConfig(url="http://167.235.0.227:2104"))

    # The query to run
    query = hypersync.Query(
        # only get block 20224332
		from_block=20224332,
        to_block=20224333,
        include_all_blocks=True,
        join_mode=JoinMode.JOIN_ALL,
        field_selection=hypersync.FieldSelection(
            block=[BlockField.NUMBER, BlockField.TIMESTAMP, BlockField.HASH],
            log=[
                LogField.LOG_INDEX,
                LogField.TRANSACTION_INDEX,
                LogField.TRANSACTION_HASH,
                LogField.DATA,
                LogField.ADDRESS,
                LogField.TOPIC0,
                LogField.TOPIC1,
                LogField.TOPIC2,
                LogField.TOPIC3,
			],
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

    )

    print("Running the query...")

    # Run the query once, the query is automatically paginated so it will return when it reaches some limit (time, response size etc.)
    # there is a next_block field on the response object so we can set the from_block of our query to this value and continue our query until
    # res.next_block is equal to res.archive_height or query.to_block in case we specified an end block.
    res = await client.get(query)

    print(f"Ran the query once.  Next block to query is {res.next_block}")

    print(len(res.data.blocks))
    print(len(res.data.transactions))
    print(len(res.data.logs))

asyncio.run(main())