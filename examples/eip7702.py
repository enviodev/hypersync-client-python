## NOTE : not all hypersync sources have this data, if no data returned and you're expecting it to - please let the team know in discord.

import hypersync
import asyncio
from hypersync import  TransactionField, ClientConfig

async def main():
    client = hypersync.HypersyncClient(ClientConfig())

    # The query to run
    query = hypersync.Query(
        # only get block a small block range
        from_block=22490287,
        to_block=22490297,
        transactions=[hypersync.TransactionSelection(authorization_list=[hypersync.AuthorizationSelection(address=["0x80296ff8d1ed46f8e3c7992664d13b833504c2bb"])])],
        # TODO: add example with chain_id once operational
        field_selection=hypersync.FieldSelection(
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

    for transaction in res.data.transactions:
        print("transaction: ", transaction.hash) 
        for auth in transaction.authorization_list:
            print("  auth: ")
            print("    chain_id: ", auth.chain_id)
            print("    address: ", auth.address)
            print("    nonce: ", auth.nonce)
            print("    y_parity: ", auth.y_parity)
            print("    r: ", auth.r)
            print("    s: ", auth.s)

    print(len(res.data.logs))

asyncio.run(main())
