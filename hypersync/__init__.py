from .hypersync import HypersyncClient as _HypersyncClient
from .hypersync import Decoder as _Decoder
from typing import Optional, Dict
from dataclasses import dataclass, asdict
from strenum import StrEnum

class Decoder:
    def __init__(self, signatures: list[str]):
        self.inner = _Decoder(signatures)
    
    def enable_checksummed_addresses(self):
        self.inner.enable_checksummed_addresses()

    def disable_checksummed_addresses(self):
        self.inner.disable_checksummed_addresses()

    async def decode_logs(self, logs: any) -> any:
        return await self.inner.decode_logs(logs)

    def decode_logs_sync(self, logs: any) -> any:
        return self.inner.decode_logs_sync(logs)
    
    async def decode_events(self, events: any) -> any:
        return await self.inner.decode_events(events)

    def decode_events_sync(self, events: any) -> any:
        return self.inner.decode_events_sync(events)

class DataType(StrEnum):
    UINT64 = 'uint64'
    UINT32 = 'uint32'
    INT64 = 'int64'
    INT32 = 'int32'
    FLOAT32 = 'float32'
    FLOAT64 = 'float64'

class BlockField(StrEnum):
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
    BLOB_GAS_USED = 'blob_gas_used'
    EXCESS_BLOB_GAS = 'excess_blob_gas'
    PARENT_BEACON_BLOCK_ROOT = 'parent_beacon_block_root'
    WITHDRAWALS_ROOT = 'withdrawals_root'
    WITHDRAWALS = 'withdrawals'
    L1_BLOCK_NUMBER = 'l1_block_number'
    SEND_COUNT = 'send_count'
    SEND_ROOT = 'send_root'
    MIX_HASH = 'mix_hash'

class TransactionField(StrEnum):
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
    ACCESS_LIST = 'access_list'
    MAX_FEE_PER_BLOB_GAS = 'max_fee_per_blob_gas'
    BLOB_VERSIONED_HASHES = 'blob_versioned_hashes'
    CUMULATIVE_GAS_USED = 'cumulative_gas_used'
    EFFECTIVE_GAS_PRICE = 'effective_gas_price'
    GAS_USED = 'gas_used'
    CONTRACT_ADDRESS = 'contract_address'
    LOGS_BLOOM = 'logs_bloom'
    KIND = 'type'
    ROOT = 'root'
    STATUS = 'status'
    Y_PARITY = 'y_parity'
    L1_FEE = 'l1_fee'
    L1_GAS_PRICE = 'l1_gas_price'
    L1_GAS_USED = 'l1_gas_used'
    L1_FEE_SCALAR = 'l1_fee_scalar'
    GAS_USED_FOR_L1 = 'gas_used_for_l1'

class LogField(StrEnum):
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

class TraceField(StrEnum):
    FROM = 'from'
    TO = 'to'
    CALL_TYPE = 'call_type'
    GAS = 'gas'
    INPUT = 'input'
    INIT = 'init'
    VALUE = 'value'
    AUTHOR = 'author'
    REWARD_TYPE = 'reward_type'
    BLOCK_HASH = 'block_hash'
    BLOCK_NUMBER = 'block_number'
    ADDRESS = 'address'
    CODE = 'code'
    GAS_USED = 'gas_used'
    OUTPUT = 'output'
    SUBTRACES = 'subtraces'
    TRACE_ADDRESS = 'trace_address'
    TRANSACTION_HASH = 'transaction_hash'
    TRANSACTION_POSITION = 'transaction_position'
    TYPE = 'type'
    ERROR = 'error'

class HexOutput(StrEnum):
    NO_ENCODE = 'NoEncode'
    PREFIXED = 'Prefixed'
    NON_PREFIXED = 'NonPrefixed'

@dataclass
class LogSelection:
    address: Optional[list[str]] = None
    topics: Optional[list[list[str]]] = None

@dataclass
class TransactionSelection:
    from_: Optional[list[str]] = None
    to: Optional[list[str]] = None
    sighash: Optional[list[str]] = None
    status: Optional[int] = None
    kind: Optional[list[str]] = None
    contract_address: Optional[list[str]] = None

@dataclass
class TraceSelection:
    from_: Optional[list[str]] = None
    to: Optional[list[str]] = None
    call_type: Optional[list[str]] = None
    reward_type: Optional[list[str]] = None
    kind: Optional[list[str]] = None
    sighash: Optional[list[str]] = None

@dataclass
class FieldSelection:
    block: Optional[list[BlockField]] = None
    transaction: Optional[list[TransactionField]] = None
    log: Optional[list[LogField]] = None
    trace: Optional[list[TraceField]] = None

@dataclass
class Query:
    from_block: int
    field_selection: FieldSelection
    to_block: Optional[int] = None
    logs: Optional[list[LogSelection]] = None
    transactions: Optional[list[TransactionSelection]] = None
    traces: Optional[list[TraceSelection]] = None
    include_all_blocks: Optional[bool] = None
    max_num_blocks: Optional[int] = None
    max_num_transactions: Optional[int] = None
    max_num_logs: Optional[int] = None
    max_num_traces: Optional[int] = None

@dataclass
class ColumnMapping:
    block: Optional[Dict[BlockField, DataType]] = None
    transaction: Optional[Dict[TransactionField, DataType]] = None
    log: Optional[Dict[LogField, DataType]] = None
    trace: Optional[Dict[TraceField, DataType]] = None
    decoded_log: Optional[Dict[str, DataType]] = None

@dataclass
class StreamConfig:
    column_mapping: Optional[ColumnMapping] = None
    event_signature: Optional[str] = None
    hex_output: Optional[HexOutput] = None
    batch_size: Optional[int] = None
    concurrency: Optional[int] = None
    max_num_blocks: Optional[int] = None
    max_num_transactions: Optional[int] = None
    max_num_logs: Optional[int] = None
    max_num_traces: Optional[int] = None

@dataclass
class ClientConfig:
    url: Optional[str] = None
    bearer_token: Optional[str] = None
    http_req_timeout_millis: Optional[int] = None
    max_num_retries: Optional[int] = None
    retry_backoff_ms: Optional[int] = None
    retry_base_ms: Optional[int] = None
    retry_ceiling_ms: Optional[int] = None

class HypersyncClient:
    def __init__(self, config: ClientConfig):
        self.inner = _HypersyncClient(asdict(config))

    async def get_height(self) -> int:
        return await self.inner.get_height()
    
    async def collect(self, query: Query, config: StreamConfig) -> any:
        return await self.inner.collect(asdict(query), asdict(config))
    
    async def collect_events(self, query: Query, config: StreamConfig) -> any:
        return await self.inner.collect_events(asdict(query), asdict(config))
    
    async def collect_arrow(self, query: Query, config: StreamConfig) -> any:
        return await self.inner.collect_arrow(asdict(query), asdict(config))
    
    async def collect_parquet(self, path: str, query: Query, config: StreamConfig) -> None:
        return await self.inner.collect_parquet(path, asdict(query), asdict(config))

    async def get(self, query: Query) -> any:
        return await self.inner.get(asdict(query))
    
    async def get_events(self, query: Query) -> any:
        return await self.inner.get_events(asdict(query))
    
    async def get_arrow(self, query: Query) -> any:
        return await self.inner.get_arrow(asdict(query))
    
    async def stream(self, query: Query, config: StreamConfig) -> any:
        return await self.inner.stream(asdict(query), asdict(config))
    
    async def stream_events(self, query: Query, config: StreamConfig) -> any:
        return await self.inner.stream_events(asdict(query), asdict(config))
    
    async def stream_arrow(self, query: Query, config: StreamConfig) -> any:
        return await self.inner.stream_arrow(asdict(query), asdict(config))

def preset_query_blocks_and_transactions(from_block: int, to_block: Optional[int] = None) -> Query:
    return Query(
        from_block=from_block,
        to_block=to_block,
        include_all_blocks=True,
        transactions=[TransactionSelection()],
        field_selection=FieldSelection(
            block=[e.value for e in BlockField],
            transaction=[e.value for e in TransactionField],
        )
    )

def preset_query_blocks_and_transaction_hashes(from_block: int, to_block: Optional[int] = None) -> Query:
    return Query(
        from_block=from_block,
        to_block=to_block,
        include_all_blocks=True,
        transactions=[TransactionSelection()],
        field_selection=FieldSelection(
            block=[e.value for e in BlockField],
            transaction=[
                TransactionField.BLOCK_HASH,
                TransactionField.BLOCK_NUMBER,
                TransactionField.HASH,
            ],
        )
    )

def preset_query_logs(address: str, from_block: int, to_block: Optional[int] = None) -> Query:
    return Query(
        from_block=from_block,
        to_block=to_block,
        logs=[LogSelection(address=[address])],
        field_selection=FieldSelection(
            log=[e.value for e in LogField]
        )
    )

def preset_query_logs_of_event(address: str, topic0: str, from_block: int, to_block: Optional[int] = None) -> Query:
    return Query(
        from_block=from_block,
        to_block=to_block,
        logs=[LogSelection(
            address=[address],
            topics=[[topic0]]
        )],
        field_selection=FieldSelection(
            log=[e.value for e in LogField]
        )
    )
