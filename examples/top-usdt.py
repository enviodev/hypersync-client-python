import hypersync
from hypersync import LogSelection, LogField, DataType, FieldSelection, ColumnMapping, TransactionField
import asyncio
import polars

async def collect_events():
    client = hypersync.HypersyncClient(hypersync.ClientConfig())

    height = await client.get_height()

    query = hypersync.Query(
        # start from 10k blocks back
        from_block=height-int(1e4),
        # Select the logs we want
        logs=[LogSelection(
            address=["0xdAC17F958D2ee523a2206206994597C13D831ec7"],
            topics=[["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]],
        )],
        # Select the fields and tables we want
        field_selection=FieldSelection(
            log=[
                LogField.TOPIC0,
                LogField.TOPIC1,
                LogField.TOPIC2,
                LogField.DATA,
                LogField.TRANSACTION_HASH,
            ],
            transaction=[
                TransactionField.HASH,
                TransactionField.GAS_USED,
            ]
        ),
    )

    config = hypersync.StreamConfig(
        hex_output=hypersync.HexOutput.PREFIXED,
        column_mapping=ColumnMapping(
            # map value columns to float so we can do calculations with them
            decoded_log={
                "value": DataType.FLOAT64,
            },
            transaction={
                TransactionField.GAS_USED: DataType.FLOAT64,
            },
        ),
        # give event signature so client can decode logs into decoded_logs.parquet file
        event_signature="Transfer(address indexed from, address indexed to, uint256 value)",
    )

    await client.collect_parquet("data", query, config)

def analyze_events():
    # read raw logs
    logs = polars.read_parquet(
        "data/logs.parquet",
    )

    # read transactions
    transactions = polars.read_parquet(
        "data/transactions.parquet",
    )
    
    # read decoded logs and join(stack) the rows with raw logs.
    # then join transactions using the tx hash column from raw logs table.
    data = polars.read_parquet(
        "data/decoded_logs.parquet"
    ).hstack(logs).join(
        other=transactions,
        left_on=polars.col("transaction_hash"),
        right_on=polars.col("hash"),
    ).group_by(
        polars.col("from")
    ).agg(
        polars.col("value").sum().alias("total_value_sent"),
        polars.col("gas_used").sum().alias("total_gas_used"),
    ).sort(
        polars.col("total_value_sent"),
        descending=True
    ).limit(10)

    polars.Config.set_ascii_tables()
    polars.Config.set_tbl_width_chars(100)
    polars.Config.set_fmt_str_lengths(50)

    print(data)

asyncio.run(collect_events())
analyze_events()
