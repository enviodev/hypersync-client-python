import hypersync
from hypersync import LogSelection, LogField, DataType, FieldSelection, ColumnMapping
import asyncio
import polars

async def collect_events():
    client = hypersync.HypersyncClient()

    height = await client.get_height()

    query = hypersync.Query(
        from_block=height-int(1e4),
        logs=[LogSelection(
            address=["0xdAC17F958D2ee523a2206206994597C13D831ec7"],
            topics=[["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]],
        )],
        field_selection=FieldSelection(
            log=[
                LogField.TOPIC1,
                LogField.TOPIC2,
                LogField.DATA,
            ]
        ),
    )

    config = hypersync.ParquetConfig(
        path="data",
        hex_output=True,
        column_mapping=ColumnMapping(
            decoded_log={
                "value": DataType.FLOAT64,
            }
        ),
        event_signature="Transfer(address indexed from, address indexed to, uint256 value)",
    )

    await client.create_parquet_folder(query, config)

def analyze_events():
    data = polars.read_parquet(
        "data/decoded_logs.parquet"
    ).select(
        polars.col("*")
    ).group_by(
        polars.col("from")
    ).agg(
        polars.col("value").sum().alias("total_value_sent")
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
