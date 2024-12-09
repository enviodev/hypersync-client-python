import hypersync
import asyncio
from hypersync import BlockField, TransactionField, LogField, ClientConfig

# For a simpler example with a single event, see all-erc20-transfers.py

transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
approval_topic = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"

async def main():
    client = hypersync.HypersyncClient(ClientConfig())

    # The query to run
    query = hypersync.Query(
        # start from block 0 and go to the end of the chain (we don't specify a toBlock).
        from_block=0,
        # The logs we want. We will also automatically get transactions and blocks relating to these logs (the query implicitly joins them).
        logs=[
            hypersync.LogSelection(
                # We want All ERC20 transfers so no address filter and only a filter for the first topic
                topics=[
                    [
                        transfer_topic
                    ],
                ]
            ),
            #  We need to place the approvals topic in a separate log selection so that it acts as an OR (logical).
            hypersync.LogSelection(
                # We want All ERC20 approvals so no address filter and only a filter for the first topic
                topics=[
                    [
                        approval_topic
                    ],
                ]
            )
        ],
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
            ],
        ),
    )

    # start the stream
    receiver = await client.stream(query, hypersync.StreamConfig())

    decoder = hypersync.Decoder(
        ["Transfer(address indexed from, address indexed to, uint256 value)", "Approval(address indexed owner, address indexed spender, uint256 value)"]
    )

    # Let's count total volume, it is meaningless because of currency differences but good as an example.
    total_volume = 0
    total_approvals = 0

    while True:
        res = await receiver.recv()
        # exit if the stream finished
        if res is None:
            break

        # Decode the log on a background thread so we don't block the event loop.
        # Can also use decoder.decode_logs_sync if it is more convenient.
        decoded_logs = await decoder.decode_logs(res.data.logs)

        # Loop through each log in res.data.logs and get the index of the decoded data in decoded_logs.
        for index, log in enumerate(res.data.logs):
            # Skip invalid logs
            if log is None:
                continue

            # Determine the type of log based on the event signature
            event_signature = log.topics[0]  # Assuming this attribute exists

            decoded_log = decoded_logs[index]

            if decoded_log is None:
                # We can't decode events with the wrong number of indexed arguments (even if the topic is correct)
                continue

            if event_signature == transfer_topic:
                total_volume += decoded_log.body[0].val
            elif event_signature == approval_topic:
                total_approvals += decoded_log.body[0].val
            else:
                print(f"Unknown event signature: {event_signature}")
        
        total_blocks = res.next_block - query.from_block
        print(f"reached block {res.next_block}")
        print(f"total volume was {total_volume} and total approvals were {total_approvals} in {total_blocks} blocks")

asyncio.run(main())
