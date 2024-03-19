import hypersync
import asyncio
from hypersync import BlockField, TransactionField, LogField

async def main():
    # Create hypersync client using the arbitrum hypersync endpoint
    client = hypersync.HypersyncClient("https://arbitrum.hypersync.xyz")

    # The query to run
    query = hypersync.Query(
		# start from block 0 and go to the end of the chain (we don't specify a toBlock).
		from_block=0,
        # The logs we want. We will also automatically get transactions and blocks relating to these logs (the query implicitly joins them).
		logs=[hypersync.LogSelection(
            # We want All ERC20 transfers so no address filter and only a filter for the first topic
            topics=[["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]]
		)],
        # Select the fields we are interested in, notice topics are selected as topic0,1,2,3
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
		)
    )

    print("Running the query...")

    # Run the query once, the query is automatically paginated so it will return when it reaches some limit (time, response size etc.)
    # there is a next_block field on the response object so we can set the from_block of our query to this value and continue our query until
    # res.next_block is equal to res.archive_height or query.to_block in case we specified an end block.
    res = await client.send_req(query)

    print(f"Ran the query once.  Next block to query is {res.next_block}")

    # read json abi file for erc20
    with open('./erc20.abi.json', 'r') as json_file:
        abi = json_file.read()

    # Map of contract_address -> abi
    abis = {}

    # every log we get should be decodable by this abi but we don't know
    # the specific contract addresses since we are indexing all erc20 transfers.
    for log in res.data.logs:
        abis[log.address] = abi

    # Create a decoder with our mapping
    decoder = hypersync.Decoder(abis)

    # Decode the log on a background thread so we don't block the event loop.
    # Can also use decoder.decode_logs_sync if it is more convenient.
    decoded_logs = await decoder.decode_logs(res.data.logs)

    # Let's count total volume, it is meaningless because of currency differences but good as an example.
    total_volume = 0
    for log in decoded_logs:
        total_volume += log.body[0]
    
    total_blocks = res.next_block - query.from_block

    print(f"total volume was {total_volume} in {total_blocks} blocks")


asyncio.run(main())