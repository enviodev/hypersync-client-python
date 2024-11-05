import hypersync
import asyncio
import time
import logging
import datetime
from hypersync import ClientConfig
from tqdm_loggable.auto import tqdm
from tqdm_loggable.tqdm_logging import tqdm_logging

# Set up logging
logger = logging.getLogger(__name__)
fmt = "%(filename)-20s:%(lineno)-4d %(asctime)s %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt,
                    handlers=[logging.StreamHandler()])

# Configure tqdm logging
tqdm_logging.set_level(logging.INFO)
tqdm_logging.set_log_rate(datetime.timedelta(seconds=5))


async def main():
    client = hypersync.HypersyncClient(ClientConfig())
    height = await client.get_height()
    start_block = height - 8000
    total_blocks = height - start_block

    query = hypersync.preset_query_blocks_and_transactions(start_block, height)

    # start the stream
    receiver = await client.stream(query, hypersync.StreamConfig())

    print(f"Starting the stream from block {start_block} to {height}...")
    start_time = time.time()
    total_processed_blocks = 0
    total_transactions = 0

    with tqdm(total=total_blocks, desc="Processing blocks", unit="blocks") as pbar:
        while True:
            res = await receiver.recv()
            # exit if the stream finished
            if res is None:
                break

            blocks_in_batch = len(res.data.blocks)
            total_processed_blocks += blocks_in_batch
            total_transactions += len(res.data.transactions)

            # Update progress bar
            pbar.update(blocks_in_batch)
            pbar.set_postfix({
                "Current height": res.next_block,
                "Transactions": total_transactions
            })

    end_time = time.time()
    duration = end_time - start_time

    print("\nStream completed!")
    print(f"Total time taken: {duration:.2f} seconds")
    print(f"Total blocks processed: {total_processed_blocks}")
    print(f"Total transactions processed: {total_transactions}")

if __name__ == "__main__":
    asyncio.run(main())
