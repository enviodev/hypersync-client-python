import hypersync
import asyncio
from hypersync import BlockField, TransactionField, LogField

# the addresses we want to get data for
addresses = [
    "0xD1a923D70510814EaE7695A76326201cA06d080F".lower(),
    "0xc0A101c4E9Bb4463BD2F5d6833c2276C36914Fb6".lower(),
    "0xa0FBaEdC4C110f5A0c5E96c3eeAC9B5635b74CE7".lower(),
    "0x32448eb389aBe39b20d5782f04a8d71a2b2e7189".lower(),
]


# Convert address to topic for filtering. Padds the address with zeroes.
def address_to_topic(address):
    return "0x000000000000000000000000" + address[2:]


async def main():
    # Create hypersync client using the mainnet hypersync endpoint (default)
    client = hypersync.HypersyncClient()

    address_topic_filter = list(map(address_to_topic, addresses))

    # The query to run
    query = hypersync.Query(
        from_block=0,
        # The logs we want. We will also automatically get transactions and blocks relating to these logs (the query implicitly joins them).
        logs=[
            hypersync.LogSelection(
                # We want All ERC20 transfers coming to any of our addresses
                topics=[
                    [
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ],
                    [],
                    address_topic_filter,
                    [],
                ],
            ),
            hypersync.LogSelection(
                # We want All ERC20 transfers going from any of our addresses
                topics=[
                    [
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ],
                    address_topic_filter,
                    [],
                    [],
                ]
            ),
        ],
        transactions=[
            # get all transactions coming from and going to any of our addresses.
			hypersync.TransactionSelection(from_=addresses),
			hypersync.TransactionSelection(to=addresses),
		],
        # Select the fields we are interested in, notice topics are selected as topic0,1,2,3
        field_selection=hypersync.FieldSelection(
			block=[
				BlockField.NUMBER,
				BlockField.TIMESTAMP,
				BlockField.HASH,
			],
			log=[
				LogField.BLOCK_NUMBER,
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
    with open("./erc20.abi.json", "r") as json_file:
        abi = json_file.read()

    # Map of contract_address -> abi
    abis = {}

    # every log we get should be decodable by this abi but we don't know
    # the specific contract addresses since we are indexing all erc20 transfers.
    for log in res.data.logs:
        abis[log.address] = abi

    # Create a decoder with out mapping
    decoder = hypersync.Decoder(abis)

    # Decode the log on a background thread so we don't block the event loop.
    # Can also use decoder.decode_logs_sync if it is more convenient.
    decoded_logs = await decoder.decode_logs(res.data.logs)

    # Let's count total volume for each address, it is meaningless because of currency differences but good as an example.
    total_erc20_volume = {}

    for log in decoded_logs:
        # Check if the keys exist in the dictionary, if not, initialize them with 0
        total_erc20_volume[log.indexed[0]] = total_erc20_volume.get(log.indexed[0], 0)
        total_erc20_volume[log.indexed[1]] = total_erc20_volume.get(log.indexed[1], 0)

        # We count for both sides but we will filter by our addresses later
        # so we will ignore unnecessary addresses.
        total_erc20_volume[log.indexed[0]] += log.body[0]
        total_erc20_volume[log.indexed[1]] += log.body[0]

    for address in addresses:
        erc20_volume = total_erc20_volume.get(address, 0)
        print(f"total erc20 transfer voume for address {address} is {erc20_volume}")

    total_wei_volume = {}
    for tx in res.data.transactions:
        # `from` is reserved in python so hypersync uses `from_`
        total_wei_volume[tx.from_] = total_wei_volume.get(tx.from_, 0)
        total_wei_volume[tx.to] = total_wei_volume.get(tx.to, 0)

        total_wei_volume[tx.from_] += int(tx.value, 16)
        total_wei_volume[tx.to] += int(tx.value, 16)

    for address in addresses:
        print(
            f"total wei transfer volume for address {address} is {total_wei_volume.get(address, 0)}"
        )


asyncio.run(main())
