import os
from dotenv import load_dotenv
import hypersync
import asyncio
import polars

# Load environment variables from a .env file
load_dotenv()

async def run():
    bearer_token = os.getenv("ENVIO_API_TOKEN")
    if not bearer_token:
        raise ValueError("ENVIO_API_TOKEN environment variable is required. Please set it in your .env file.")
    
    client = hypersync.HypersyncClient(
        hypersync.ClientConfig(
            url="https://eth.hypersync.xyz/",
            bearer_token=bearer_token
        )
    )

    res = await client.collect_arrow(
        hypersync.Query(
            # This is the block that POS ugrade happened on eth mainnet
            from_block=15537394,
            # Get all blocks this address mined, and get all associated transactions
            blocks=[
                hypersync.BlockSelection(
                    miner=["0xe43Cc5b6FF052f5Aa931A4F9eF2bfA0C500014CA"]
                )
            ],
            join_mode=hypersync.JoinMode.JOIN_ALL,
            field_selection=hypersync.FieldSelection(
                block=[
                    hypersync.BlockField.MINER,
                    hypersync.BlockField.BASE_FEE_PER_GAS,
                    hypersync.BlockField.GAS_USED,
                ],
                transaction=[
                    hypersync.TransactionField.EFFECTIVE_GAS_PRICE,
                    hypersync.TransactionField.GAS_USED,
                ],
            ),
        ),
        hypersync.StreamConfig(
            hex_output=hypersync.HexOutput.PREFIXED,
            column_mapping=hypersync.ColumnMapping(
                transaction={
                    hypersync.TransactionField.EFFECTIVE_GAS_PRICE: hypersync.DataType.UINT64,
                    hypersync.TransactionField.GAS_USED: hypersync.DataType.UINT64,
                },
                block={
                    hypersync.BlockField.BASE_FEE_PER_GAS: hypersync.DataType.UINT64,
                    hypersync.BlockField.GAS_USED: hypersync.DataType.UINT64,
                },
            ),
        ),
    )

    transactions = polars.from_arrow(res.data.transactions)

    effective_gas_price = transactions.get_column("effective_gas_price")
    gas_used = transactions.get_column("gas_used")

    total_tx_fee = (effective_gas_price * gas_used).sum()

    print("total_tx_fee ", total_tx_fee)

    blocks = polars.from_arrow(res.data.blocks)

    base_fee_per_gas = blocks.get_column("base_fee_per_gas")
    block_gas_used = blocks.get_column("gas_used")

    burned_fee = (base_fee_per_gas * block_gas_used).sum()

    print("burned_fee ", burned_fee)

    print("reward: ", total_tx_fee - burned_fee)


asyncio.run(run())
