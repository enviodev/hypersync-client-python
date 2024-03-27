from .hypersync import HypersyncClient as _HypersyncClient
from .hypersync import Decoder as _Decoder
from typing import Optional, Dict
from dataclasses import dataclass, asdict
from strenum import StrEnum

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
    CUMULATIVE_GAS_USED = 'cumulative_gas_used'
    EFFECTIVE_GAS_PRICE = 'effective_gas_price'
    GAS_USED = 'gas_used'
    CONTRACT_ADDRESS = 'contract_address'
    LOGS_BLOOM = 'logs_bloom'
    TYPE = 'type'
    ROOT = 'root'
    STATUS = 'status'
    SIGHASH = 'sighash'

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

@dataclass
class TraceSelection:
    from_: Optional[list[str]] = None
    to: Optional[list[str]] = None
    call_type: Optional[list[str]] = None
    reward_type: Optional[list[str]] = None
    type_: Optional[list[str]] = None
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
class ParquetConfig:
    path: str
    hex_output: Optional[bool] = None
    batch_size: Optional[int] = None
    concurrency: Optional[int] = None
    retry: Optional[bool] = None
    column_mapping: Optional[ColumnMapping] = None
    event_signature: Optional[str] = None

class HypersyncClient:
    def __init__(self, url="https://eth.hypersync.xyz", bearer_token=None, http_req_timeout_millis=None):
        self.inner = _HypersyncClient({
            "url": url,
            "bearer_token": bearer_token,
            "http_req_timeout_millis": http_req_timeout_millis
        })

    async def get_height(self) -> int:
        return await self.inner.get_height()

    async def create_parquet_folder(self, query: Query, config: ParquetConfig) -> None:
        return await self.inner.create_parquet_folder(asdict(query), asdict(config))

    async def send_req(self, query: Query) -> any:
        return await self.inner.send_req(asdict(query))

    async def send_events_req(self, query: Query) -> any:
        return await self.inner.send_events_req(asdict(query))

    async def send_req_arrow(self, query: Query) -> any:
        return await self.inner.send_req_arrow(asdict(query))
    
    def preset_query_blocks_and_transactions(self, from_block: int, to_block: Optional[int]) -> Query:
        query = self.inner.preset_query_blocks_and_transactions(from_block, to_block)
        return dict_to_query(query)
    
    def preset_query_blocks_and_transaction_hashes(self, from_block: int, to_block: Optional[int]) -> Query:
        query = self.inner.preset_query_blocks_and_transaction_hashes(from_block, to_block)
        return dict_to_query(query)
    
    def preset_query_logs(self, contract_address: str, from_block: int, to_block: Optional[int]) -> Query:
        query = self.inner.preset_query_logs(contract_address, from_block, to_block)
        return dict_to_query(query)
    
    def preset_query_logs_of_event(self, contract_address: str, topic0: str, from_block: int, to_block: Optional[int]) -> Query:
        query = self.inner.preset_query_logs_of_event(contract_address, topic0, from_block, to_block)
        return dict_to_query(query)

# helper function for converting a Query object from the rust side interpreted as a dict into a 
# dataclass Query
def dict_to_query(data: dict) -> Query:
    logs = [LogSelection(**log) for log in data.get('logs', [])] if 'logs' in data else None
    transactions = [TransactionSelection(**txn) for txn in data.get('transactions', [])] if 'transactions' in data else None
    traces = [TraceSelection(**trace) for trace in data.get('traces', [])] if 'traces' in data else None
    
    field_selection = FieldSelection(
        block=[BlockField(block) for block in data['field_selection'].get('block', [])] if 'block' in data['field_selection'] else None,
        transaction=[TransactionField(txn) for txn in data['field_selection'].get('transaction', [])] if 'transaction' in data['field_selection'] else None,
        log=[LogField(log) for log in data['field_selection'].get('log', [])] if 'log' in data['field_selection'] else None,
        trace=[TraceField(trace) for trace in data['field_selection'].get('trace', [])] if 'trace' in data['field_selection'] else None,
    )
    
    return Query(
        from_block=data['from_block'],
        to_block=data.get('to_block'),
        logs=logs,
        transactions=transactions,
        traces=traces,
        include_all_blocks=data.get('include_all_blocks'),
        max_num_blocks=data.get('max_num_blocks'),
        max_num_transactions=data.get('max_num_transactions'),
        max_num_logs=data.get('max_num_logs'),
        max_num_traces=data.get('max_num_traces'),
        field_selection=field_selection,
    )