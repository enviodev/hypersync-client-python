from .hypersync import HypersyncClient as _HypersyncClient
from .hypersync import Decoder as _Decoder
from typing import TypedDict, Optional, Dict
import enum

class Decoder:
    def __init__(self, json_abis: Dict[str, str]):
        self.inner = _Decoder(json_abis)
    
    async def decode_logs(self, logs: any) -> any:
        return await self.inner.decode_logs(logs)

    def decode_logs_sync(self, logs: any) -> any:
        return self.inner.decode_logs_sync(logs)
    
    async def decode_events(self, events: any) -> any:
        return await self.inner.decode_events(events)

    def decode_events_sync(self, events: any) -> any:
        return self.inner.decode_events_sync(events)

class DataType(enum.StrEnum):
    UINT64 = 'uint64'
    UINT32 = 'uint32'
    INT64 = 'int64'
    INT32 = 'int32'
    FLOAT32 = 'float32'
    FLOAT64 = 'float64'

class BlockField(enum.StrEnum):
    NUMBER = 'number'
    HASH = 'hash'
    PARENT_HASH = 'parent_hash'
    NONCE = 'nonce'
    SHA3_UNCLES = 'sha3_uncles'
    LOGS_BLOOM = 'logs_bloom'
    TRANSACTIONS_ROOT = 'transactions_root'
    STATE_ROOT = 'state_root'
    RECEIPTS_ROOT = 'receipts_root'
    MINER = 'miner'
    DIFFICULTY = 'difficulty'
    TOTAL_DIFFICULTY = 'total_difficulty'
    EXTRA_DATA = 'extra_data'
    SIZE = 'size'
    GAS_LIMIT = 'gas_limit'
    GAS_USED = 'gas_used'
    TIMESTAMP = 'timestamp'
    UNCLES = 'uncles'
    BASE_FEE_PER_GAS = 'base_fee_per_gas'

class TransactionField(enum.StrEnum):
    BLOCK_HASH = 'block_hash'
    BLOCK_NUMBER = 'block_number'
    FROM = 'from'
    GAS = 'gas'
    GAS_PRICE = 'gas_price'
    HASH = 'hash'
    INPUT = 'input'
    NONCE = 'nonce'
    TO = 'to'
    TRANSACTION_INDEX = 'transaction_index'
    VALUE = 'value'
    V = 'v'
    R = 'r'
    S = 's'
    MAX_PRIORITY_FEE_PER_GAS = 'max_priority_fee_per_gas'
    MAX_FEE_PER_GAS = 'max_fee_per_gas'
    CHAIN_ID = 'chain_id'
    CUMULATIVE_GAS_USED = 'cumulative_gas_used'
    EFFECTIVE_GAS_PRICE = 'effective_gas_price'
    CONTRACT_ADDRESS = 'contract_address'
    LOGS_BLOOM = 'logs_bloom'
    TYPE = 'type'
    ROOT = 'root'
    STATUS = 'status'
    SIGHASH = 'sighash'

class LogField(enum.StrEnum):
    REMOVED = 'removed'
    LOG_INDEX = 'log_index'
    TRANSACTION_INDEX = 'transaction_index'
    TRANSACTION_HASH = 'transaction_hash'
    BLOCK_HASH = 'block_hash'
    BLOCK_NUMBER = 'block_number'
    ADDRESS = 'address'
    DATA = 'data'
    TOPIC0 = 'topic0'
    TOPIC1 = 'topic1'
    TOPIC2 = 'topic2'
    TOPIC3 = 'topic3'

class TraceField(enum.StrEnum):
    FROM = 'from'
    TO = 'to'
    CALL_TYPE = 'call_type'
    GAS = 'gas'
    INPUT = 'input'
    VALUE = 'value'
    REWARD_TYPE = 'reward_type'
    BLOCK_HASH = 'block_hash'
    BLOCK_NUMBER = 'block_number'
    GAS_USED = 'gas_used'
    OUTPUT = 'output'
    SUBTRACES = 'subtraces'
    TRACE_ADDRESS = 'trace_address'
    TRANSACTION_HASH = 'transaction_hash'
    TRANSACTION_POSITION = 'transaction_position'
    TYPE = 'type'
    ERROR = 'error'
    SIGHASH = 'sighash'

class LogSelection(TypedDict):
    address: Optional[list[str]]
    topics: Optional[list[list[str]]]

class TransactionSelection(TypedDict):
    from_: Optional[list[str]]
    to: Optional[list[str]]
    sighash: Optional[list[str]]
    status: Optional[int]

class TraceSelection(TypedDict):
    from_: Optional[list[str]]
    to: Optional[list[str]]
    call_type: Optional[list[str]]
    reward_type: Optional[list[str]]
    type_: Optional[list[str]]
    sighash: Optional[list[str]]

class FieldSelection:
    block: Optional[list[BlockField]]
    transaction: Optional[list[TransactionField]]
    log: Optional[list[LogField]]
    trace: Optional[list[TraceField]]

class Query(TypedDict):
    from_block: int
    to_block: Optional[int]
    logs: Optional[list[LogSelection]]
    include_all_blocks: Optional[bool]
    field_selection: FieldSelection
    max_num_blocks: Optional[int]
    max_num_transactions: Optional[int]
    max_num_logs: Optional[int]
    max_num_traces: Optional[int]

class ColumnMapping(TypedDict):
    block: Dict[BlockField, DataType]
    transaction: Dict[TransactionField, DataType]
    log: Dict[LogField, DataType]
    trace: Dict[TraceField, DataType]

class ParquetConfig(TypedDict):
    path: str
    hex_output: Optional[bool]
    batch_size: Optional[int]
    concurrency: Optional[int]
    retry: Optional[bool]
    column_mapping: Optional[ColumnMapping]

class HypersyncClient:
    def __init__(self, url="https://eth.hypersync.xyz", bearer_token=None, http_req_timeout_millis=None):
        self.inner = _HypersyncClient({
            "url": url,
            "bearer_token": bearer_token,
            "http_req_timeout_millis": http_req_timeout_millis
        })

    async def get_height(self) -> int:
        return await self.inner.get_height()

    async def create_parquet_folder(self, query: Query, config: ParquetConfig) -> any:
        return await self.inner.create_parquet_folder(query, config)

    async def send_req(self, query: Query) -> any:
        return await self.inner.send_req(query)

    async def send_events_req(self, query: Query) -> any:
        return await self.inner.send_events_req(query)
