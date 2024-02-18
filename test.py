import hypersync
import asyncio
import time
from hypersync import DataType, BlockField, TransactionField, LogField, TraceField

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
                # We want ERC20 transfers
                ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
                [],
                # We want the transfers that go to this address.
                # appending zeroes because topic is 32 bytes but address is 20 bytes
                ["0x000000000000000000000000" + ADDR],
            ]
        ),
        hypersync.LogSelection(
            topics=[
                # We want ERC20 transfers
                ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
                # We want the transfers that go to this address.
                # appending zeroes because topic is 32 bytes but address is 20 bytes
                ["0x000000000000000000000000" + ADDR],
                [],
            ],
        )
    ],
    transactions=[
        hypersync.TransactionSelection(
            from_=["0x" + ADDR]
        ),
        hypersync.TransactionSelection(
            to=["0x" + ADDR]
        ),
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
    )
)

async def test_create_parquet_folder():
    client = hypersync.HypersyncClient()
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()

        await client.create_parquet_folder(
            QUERY, hypersync.ParquetConfig(
                path="data",
                retry=True,
                hex_output=True,
                column_mapping=hypersync.ColumnMapping(
                    trace={
                        TraceField.TRANSACTION_POSITION: DataType.INT32,
                    },
                    transaction={
                        TransactionField.BLOCK_NUMBER: DataType.INT64,
                        TransactionField.VALUE: DataType.FLOAT32,
                    }
                )
            )
        )
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    avg_time = total_time / NUM_BENCHMARK_RUNS
    print(f"create_parquet_folder time: {format(execution_time, '.9f')}ms")


async def test_send_req():
    client = hypersync.HypersyncClient()
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        res = await client.send_req(QUERY)
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    avg_time = total_time / NUM_BENCHMARK_RUNS
    print(f"send_req time: {format(execution_time, '.9f')}ms")


async def test_send_events_req():
    client = hypersync.HypersyncClient()
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        res = await client.send_events_req(QUERY)
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    avg_time = total_time / NUM_BENCHMARK_RUNS
    print(f"send_events_req time: {format(execution_time, '.9f')}ms")


async def test_get_height():
    client = hypersync.HypersyncClient()
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        height = await client.get_height()
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    avg_time = total_time / NUM_BENCHMARK_RUNS
    print(f"get_height time: {format(execution_time, '.9f')}ms")


async def test_decode_logs():
    client = hypersync.HypersyncClient()
    res = await client.send_req(QUERY)
    with open("./erc20.abi.json", "r") as json_file:
        json = json_file.read()
    abis = {}
    for log in res.data.logs:
        abis[log.address] = json
    decoder = hypersync.Decoder(json_abis=abis)
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        decoded_logs = decoder.decode_logs_sync(res.data.logs)
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    avg_time = total_time / NUM_BENCHMARK_RUNS
    print(f"decode_logs time: {format(execution_time, '.9f')}ms")


async def test_decode_events():
    client = hypersync.HypersyncClient()
    res = await client.send_events_req(QUERY)
    with open("./erc20.abi.json", "r") as json_file:
        json = json_file.read()
    abis = {}
    for event in res.events:
        abis[event.log.address] = json
    decoder = hypersync.Decoder(abis)
    total_time = 0
    for _ in range(NUM_BENCHMARK_RUNS):
        start_time = time.time()
        decoded_events = decoder.decode_events_sync(res.events)
        execution_time = (time.time() - start_time) * 1000
        total_time += execution_time
    avg_time = total_time / NUM_BENCHMARK_RUNS
    print(f"decode_events time: {format(execution_time, '.9f')}ms")


async def main():
    print("hypersync-client-python")
    print(f"number of runs for each test: {NUM_BENCHMARK_RUNS}")
    await test_send_req()
    await test_send_events_req()
    await test_get_height()
    await test_decode_logs()
    await test_decode_events()
    await test_create_parquet_folder()


asyncio.run(main())
