import hypersync
import asyncio
import time
from hypersync import (
    DataType,
    BlockField,
    TransactionField,
    LogField,
    TraceField,
    HexOutput,
)

# for benchmarking times.  Will run the function this many times and take the
# average
NUM_BENCHMARK_RUNS = 1

# The address we want to get all ERC20 transfers and transactions for
ADDR = "1e037f97d730Cc881e77F01E409D828b0bb14de0"

QUERY = hypersync.Query(
    from_block=17123123,
    to_block=17123223,
    logs=[
        hypersync.LogSelection(
            topics=[
                ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
            ]
        ),
        hypersync.LogSelection(
            topics=[
                ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
            ],
        ),
    ],
    transactions=[
        hypersync.TransactionSelection(from_=["0x" + ADDR]),
        hypersync.TransactionSelection(to=["0x" + ADDR]),
    ],
    include_all_blocks=True,
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
        trace=[
            TraceField.TRANSACTION_HASH,
            TraceField.ERROR,
            TraceField.OUTPUT,
            TraceField.CALL_TYPE,
            TraceField.TRANSACTION_POSITION,
        ],
    ),
)


async def test_intstr_mapping():
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()

        res = await client.collect_arrow(
            QUERY,
            hypersync.StreamConfig(
                hex_output=HexOutput.PREFIXED,
                column_mapping=hypersync.ColumnMapping(
                    trace={
                        TraceField.TRANSACTION_POSITION: DataType.INT32,
                    },
                    transaction={
                        TransactionField.BLOCK_NUMBER: DataType.INT64,
                        TransactionField.VALUE: DataType.FLOAT32,
                    },
                    decoded_log={
                        "value": DataType.INTSTR,
                    },
                ),
                event_signature="Transfer(address indexed from, address indexed to, uint256 value)",
            ),
        )

        # print(res.data.decoded_logs.column("value"))

        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    print(f"intstr_mapping time: {format(execution_time, '.9f')}ms")


async def test_create_parquet_folder():
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()

        await client.collect_parquet(
            "data",
            QUERY,
            hypersync.StreamConfig(
                hex_output=HexOutput.PREFIXED,
                column_mapping=hypersync.ColumnMapping(
                    trace={
                        TraceField.TRANSACTION_POSITION: DataType.INT32,
                    },
                    transaction={
                        TransactionField.BLOCK_NUMBER: DataType.INT64,
                        TransactionField.VALUE: DataType.FLOAT32,
                    },
                    decoded_log={
                        "value": DataType.FLOAT64,
                    },
                ),
                event_signature="Transfer(address indexed from, address indexed to, uint256 value)",
            ),
        )
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    print(f"create_parquet_folder time: {format(execution_time, '.9f')}ms")


async def test_send_req():
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        await client.get(QUERY)
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    print(f"send_req time: {format(execution_time, '.9f')}ms")


async def test_send_req_arrow():
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    import pyarrow

    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        res = await client.get_arrow(QUERY)
        execution_time = (time.time() - start_time) * 1000
        assert type(res.data.blocks) is pyarrow.lib.Table
        assert res.data.blocks._is_initialized()
        assert type(res.data.transactions) is pyarrow.lib.Table
        assert res.data.transactions._is_initialized()
        assert type(res.data.logs) is pyarrow.lib.Table
        assert res.data.logs._is_initialized()
        total_time += execution_time
    print(f"send_req_arrow time: {format(execution_time, '.9f')}ms")


async def test_send_events_req():
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        await client.get_events(QUERY)
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    print(f"send_events_req time: {format(execution_time, '.9f')}ms")


async def test_get_height():
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        await client.get_height()
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    print(f"get_height time: {format(execution_time, '.9f')}ms")


async def test_decode_logs():
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    res = await client.get(QUERY)
    decoder = hypersync.Decoder(
        ["Transfer(address indexed from, address indexed to, uint256 value)"]
    )
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        decoder.decode_logs_sync(res.data.logs)
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    print(f"decode_logs time: {format(execution_time, '.9f')}ms")


async def test_decode_events():
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    res = await client.get_events(QUERY)
    decoder = hypersync.Decoder(
        ["Transfer(address indexed from, address indexed to, uint256 value)"]
    )
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        decoder.decode_events_sync(res.data)
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    print(f"decode_events time: {format(execution_time, '.9f')}ms")


async def test_preset_query_blocks_and_transactions():
    start_time = time.time()
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    query = hypersync.preset_query_blocks_and_transactions(17_000_000, 17_000_010)
    res = await client.get(query)
    execution_time = (time.time() - start_time) * 1000
    assert len(res.data.blocks) == 10
    assert len(res.data.transactions) > 1
    print(
        f"preset_query_blocks_and_transactions time: {format(execution_time, '.9f')}ms"
    )


async def test_preset_query_blocks_and_transaction_hashes():
    start_time = time.time()
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    query = hypersync.preset_query_blocks_and_transaction_hashes(17_000_000, 17_000_010)
    res = await client.get(query)
    execution_time = (time.time() - start_time) * 1000
    assert len(res.data.blocks) == 10
    assert len(res.data.transactions) > 1
    print(
        f"preset_query_blocks_and_transaction_hashes time: {format(execution_time, '.9f')}ms"
    )


async def test_preset_query_logs():
    start_time = time.time()
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    contract_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    query = hypersync.preset_query_logs(contract_address, 17_000_000, 17_000_010)
    res = await client.get(query)
    execution_time = (time.time() - start_time) * 1000
    assert len(res.data.logs) > 1
    print(f"preset_query_logs time: {format(execution_time, '.9f')}ms")


async def test_preset_query_logs_of_event():
    start_time = time.time()
    client = hypersync.HypersyncClient(hypersync.ClientConfig())
    contract_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    topic0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    query = hypersync.preset_query_logs_of_event(
        contract_address, topic0, 17_000_000, 17_000_010
    )
    res = await client.get(query)
    execution_time = (time.time() - start_time) * 1000
    assert len(res.data.logs) > 1
    print(f"preset_query_logs_of_event time: {format(execution_time, '.9f')}ms")


def test_sig_to_topic0():
    topic0 = hypersync.signature_to_topic0(
        "FundsRetrieved(bytes32 indexed commitmentDigest,address indexed bidder,uint256 window,uint256 amount)"
    )
    assert (
        "0x4ee0e06b2d2e4d1f06e75df9f2bad2c919d860fbf843f3b1f12de3264471a102" == topic0
    )


async def main():
    print("hypersync-client-python")
    print(f"number of runs for each test: {NUM_BENCHMARK_RUNS}")
    await test_intstr_mapping()
    await test_send_req()
    await test_send_req_arrow()
    await test_send_events_req()
    await test_get_height()
    await test_decode_logs()
    await test_decode_events()
    await test_create_parquet_folder()
    await test_preset_query_blocks_and_transactions()
    await test_preset_query_blocks_and_transaction_hashes()
    await test_preset_query_logs()
    await test_preset_query_logs_of_event()
    test_sig_to_topic0()


asyncio.run(main())
