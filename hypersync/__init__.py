from .hypersync import HypersyncClient as _HypersyncClient
from .hypersync import Decoder as _Decoder
from .hypersync import CallDecoder as _CallDecoder
from .hypersync import signature_to_topic0 as _sig_to_topic0
from .hypersync import ArrowStream as _ArrowStream
from .hypersync import EventStream as _EventStream
from .hypersync import QueryResponseStream as _QueryResponseStream
from typing import Optional, Dict
from dataclasses import dataclass, asdict
from strenum import StrEnum


def signature_to_topic0(sig: str) -> str:
    return _sig_to_topic0(sig)


class Log(object):
    removed: Optional[bool]
    log_index: Optional[int]
    transaction_index: Optional[int]
    transaction_hash: Optional[str]
    block_hash: Optional[str]
    block_number: Optional[int]
    address: Optional[str]
    data: Optional[str]
    topics: Optional[str]


class AccessList(object):
    address: Optional[str]
    storage_keys: Optional[list[str]]


class Transaction(object):
    block_hash: Optional[str]
    block_number: Optional[int]
    from_: Optional[str]
    gas: Optional[str]
    gas_price: Optional[str]
    hash: Optional[str]
    input: Optional[str]
    nonce: Optional[str]
    to: Optional[str]
    transaction_index: Optional[int]
    value: Optional[str]
    v: Optional[str]
    r: Optional[str]
    s: Optional[str]
    y_parity: Optional[str]
    max_priority_fee_per_gas: Optional[str]
    max_fee_per_gas: Optional[str]
    chain_id: Optional[int]
    access_list: Optional[list[AccessList]]
    max_fee_per_blob_gas: Optional[str]
    blob_versioned_hashes: Optional[list[str]]
    cumulative_gas_used: Optional[str]
    effective_gas_price: Optional[str]
    gas_used: Optional[str]
    contract_address: Optional[str]
    logs_bloom: Optional[str]
    kind: Optional[int]
    root: Optional[str]
    status: Optional[int]
    l1_fee: Optional[str]
    l1_gas_price: Optional[str]
    l1_gas_used: Optional[str]
    l1_fee_scalar: Optional[float]
    gas_used_for_l1: Optional[str]


class Withdrawal(object):
    index: Optional[str]
    validator_index: Optional[str]
    address: Optional[str]
    amount: Optional[str]


class Block(object):
    number: Optional[int]
    hash: Optional[str]
    parent_hash: Optional[str]
    nonce: Optional[str]
    sha3_uncles: Optional[str]
    logs_bloom: Optional[str]
    transactions_root: Optional[str]
    state_root: Optional[str]
    receipts_root: Optional[str]
    miner: Optional[str]
    difficulty: Optional[str]
    total_difficulty: Optional[str]
    extra_data: Optional[str]
    size: Optional[str]
    gas_limit: Optional[str]
    gas_used: Optional[str]
    timestamp: Optional[str]
    uncles: Optional[list[str]]
    base_fee_per_gas: Optional[str]
    blob_gas_used: Optional[str]
    excess_blob_gas: Optional[str]
    parent_beacon_block_root: Optional[str]
    withdrawals_root: Optional[str]
    withdrawals: Optional[list[Withdrawal]]
    l1_block_number: Optional[int]
    send_count: Optional[str]
    send_root: Optional[str]
    mix_hash: Optional[str]


class Trace(object):
    from_: Optional[str]
    to: Optional[str]
    call_type: Optional[str]
    gas: Optional[str]
    input: Optional[str]
    init: Optional[str]
    value: Optional[str]
    author: Optional[str]
    reward_type: Optional[str]
    block_hash: Optional[str]
    block_number: Optional[int]
    address: Optional[str]
    code: Optional[str]
    gas_used: Optional[str]
    output: Optional[str]
    subtraces: Optional[int]
    trace_address: Optional[list[int]]
    transaction_hash: Optional[str]
    transaction_position: Optional[int]
    kind: Optional[str]
    error: Optional[str]


class Event(object):
    # Transaction that triggered this event
    transaction: Optional[Transaction]
    # Block that this event happened in
    block: Optional[Block]
    # Evm log data
    log: Log


class DecodedSolValue(object):
    val: any


class DecodedEvent(object):
    indexed: list[DecodedSolValue]
    body: list[DecodedSolValue]


class Decoder:
    """Decode logs parsing topics and log data."""

    def __init__(self, signatures: list[str]):
        """Initialize decoder from event signatures."""
        self.inner = _Decoder(signatures)

    def enable_checksummed_addresses(self):
        self.inner.enable_checksummed_addresses()

    def disable_checksummed_addresses(self):
        self.inner.disable_checksummed_addresses()

    async def decode_logs(self, logs: list[Log]) -> list[Optional[DecodedEvent]]:
        """Parse log and return decoded event. Returns None if topic0 not found."""
        return await self.inner.decode_logs(logs)

    def decode_logs_sync(self, logs: list[Log]) -> list[Optional[DecodedEvent]]:
        """Parse log and return decoded event. Returns None if topic0 not found."""
        return self.inner.decode_logs_sync(logs)

    async def decode_events(self, events: list[Event]) -> list[Optional[DecodedEvent]]:
        return await self.inner.decode_events(events)

    def decode_events_sync(self, events: list[Event]) -> list[Optional[DecodedEvent]]:
        return self.inner.decode_events_sync(events)


class CallDecoder:
    """Decode logs parsing topics and log data."""

    def __init__(self, signatures: list[str]):
        """Initialize decoder from event signatures."""
        self.inner = _CallDecoder(signatures)

    def enable_checksummed_addresses(self):
        self.inner.enable_checksummed_addresses()

    def disable_checksummed_addresses(self):
        self.inner.disable_checksummed_addresses()

    async def decode_inputs(self, inputs: list[str]) -> list[list[DecodedSolValue]]:
        """Parse log and return decoded event. Returns None if topic0 not found."""
        return await self.inner.decode_inputs(input)

    def decode_inputs_sync(self, inputs: list[str]) -> list[list[DecodedSolValue]]:
        """Parse log and return decoded event. Returns None if topic0 not found."""
        return self.inner.decode_input_syncs(input)

    async def decode_transactions_input(
        self, txs: list[Transaction]
    ) -> list[list[DecodedSolValue]]:
        """Parse log and return decoded event. Returns None if topic0 not found."""
        return await self.inner.decode_transactions_input(txs)

    def decode_transactions_input_sync(
        self, txs: list[Transaction]
    ) -> list[list[DecodedSolValue]]:
        """Parse log and return decoded event. Returns None if topic0 not found."""
        return self.inner.decode_transactions_input_sync(txs)

    async def decode_traces_input(
        self, traces: list[Trace]
    ) -> list[list[DecodedSolValue]]:
        """Parse log and return decoded event. Returns None if topic0 not found."""
        return await self.inner.decode_traces_input(traces)

    def decode_traces_input_sync(
        self, traces: list[Trace]
    ) -> list[list[DecodedSolValue]]:
        """Parse log and return decoded event. Returns None if topic0 not found."""
        return self.inner.decode_traces_input_sync(traces)


class DataType(StrEnum):
    """Data types supported for mapping."""

    UINT64 = "uint64"
    UINT32 = "uint32"
    INT64 = "int64"
    INT32 = "int32"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    INTSTR = "intstr"


class BlockField(StrEnum):
    """Block field enum"""

    # A scalar value equal to the number of ancestor blocks. The genesis block has a number of zero; formally Hi.
    NUMBER = "number"
    # The Keccak 256-bit hash of the block
    HASH = "hash"
    # The Keccak 256-bit hash of the parent block’s header, in its entirety; formally Hp.
    PARENT_HASH = "parent_hash"
    # A 64-bit value which, combined with the mixhash, proves that a sufficient amount of computation has been carried
    # out on this block; formally Hn.
    NONCE = "nonce"
    # The Keccak 256-bit hash of the ommers/uncles list portion of this block; formally Ho.
    SHA3_UNCLES = "sha3_uncles"
    # The Bloom filter composed from indexable information (logger address and log topics)
    # contained in each log entry from the receipt of each transaction in the transactions list;
    # formally Hb.
    LOGS_BLOOM = "logs_bloom"
    # The Keccak 256-bit hash of the root node of the trie structure populated with each
    # transaction in the transactions list portion of the block; formally Ht.
    TRANSACTIONS_ROOT = "transactions_root"
    # The Keccak 256-bit hash of the root node of the state trie, after all transactions are
    # executed and finalisations applied; formally Hr.
    STATE_ROOT = "state_root"
    # The Keccak 256-bit hash of the root node of the trie structure populated with each transaction in the
    # transactions list portion of the block; formally Ht.
    RECEIPTS_ROOT = "receipts_root"
    # The 160-bit address to which all fees collected from the successful mining of this block
    # be transferred; formally Hc.
    MINER = "miner"
    # A scalar value corresponding to the difficulty level of this block. This can be calculated
    # from the previous block’s difficulty level and the timestamp; formally Hd.
    DIFFICULTY = "difficulty"
    # The cumulative sum of the difficulty of all blocks that have been mined in the Ethereum network since the
    # inception of the network It measures the overall security and integrity of the Ethereum network.
    TOTAL_DIFFICULTY = "total_difficulty"
    # An arbitrary byte array containing data relevant to this block. This must be 32 bytes or
    # fewer; formally Hx.
    EXTRA_DATA = "extra_data"
    # The size of this block in bytes as an integer value, encoded as hexadecimal.
    SIZE = "size"
    # A scalar value equal to the current limit of gas expenditure per block; formally Hl.
    GAS_LIMIT = "gas_limit"
    # A scalar value equal to the total gas used in transactions in this block; formally Hg.
    GAS_USED = "gas_used"
    # A scalar value equal to the reasonable output of Unix’s time() at this block’s inception; formally Hs.
    TIMESTAMP = "timestamp"
    # Ommers/uncles header.
    UNCLES = "uncles"
    # A scalar representing EIP1559 base fee which can move up or down each block according
    # to a formula which is a function of gas used in parent block and gas target
    # (block gas limit divided by elasticity multiplier) of parent block.
    # The algorithm results in the base fee per gas increasing when blocks are
    # above the gas target, and decreasing when blocks are below the gas target. The base fee per gas is burned.
    BASE_FEE_PER_GAS = "base_fee_per_gas"
    # The total amount of blob gas consumed by the transactions within the block, added in EIP-4844.
    BLOB_GAS_USED = "blob_gas_used"
    # A running total of blob gas consumed in excess of the target, prior to the block. Blocks
    # with above-target blob gas consumption increase this value, blocks with below-target blob
    # gas consumption decrease it (bounded at 0). This was added in EIP-4844.
    EXCESS_BLOB_GAS = "excess_blob_gas"
    # The hash of the parent beacon block's root is included in execution blocks, as proposed by
    # EIP-4788.
    # This enables trust-minimized access to consensus state, supporting staking pools, bridges, and more.
    PARENT_BEACON_BLOCK_ROOT = "parent_beacon_block_root"
    # The Keccak 256-bit hash of the withdrawals list portion of this block.
    # See [EIP-4895](https://eips.ethereum.org/EIPS/eip-4895).
    WITHDRAWALS_ROOT = "withdrawals_root"
    # Withdrawal represents a validator withdrawal from the consensus layer.
    WITHDRAWALS = "withdrawals"
    # The L1 block number that would be used for block.number calls.
    L1_BLOCK_NUMBER = "l1_block_number"
    # The number of L2 to L1 messages since Nitro genesis.
    SEND_COUNT = "send_count"
    # The Merkle root of the outbox tree state.
    SEND_ROOT = "send_root"
    # A 256-bit hash which, combined with the nonce, proves that a sufficient amount of computation has
    # been carried out on this block; formally Hm.
    MIX_HASH = "mix_hash"


class TransactionField(StrEnum):
    """Transaction field enum"""

    # The Keccak 256-bit hash of the block
    BLOCK_HASH = "block_hash"
    # A scalar value equal to the number of ancestor blocks. The genesis block has a number of
    # zero; formally Hi.
    BLOCK_NUMBER = "block_number"
    # The 160-bit address of the message call’s sender
    FROM = "from"
    # A scalar value equal to the maximum amount of gas that should be used in executing
    # this transaction. This is paid up-front, before any computation is done and may not be increased later;
    # formally Tg.
    GAS = "gas"
    # A scalar value equal to the number of Wei to be paid per unit of gas for all computation
    # costs incurred as a result of the execution of this transaction; formally Tp.
    GAS_PRICE = "gas_price"
    # A transaction hash is a keccak hash of an RLP encoded signed transaction.
    HASH = "hash"
    # Input has two uses depending if transaction is Create or Call (if `to` field is None or
    # Some). pub init: An unlimited size byte array specifying the
    # EVM-code for the account initialisation procedure CREATE,
    # data: An unlimited size byte array specifying the
    # input data of the message call, formally Td.
    INPUT = "input"
    # A scalar value equal to the number of transactions sent by the sender; formally Tn.
    NONCE = "nonce"
    # The 160-bit address of the message call’s recipient or, for a contract creation
    # transaction, ∅, used here to denote the only member of B0 ; formally Tt.
    TO = "to"
    # Index of the transaction in the block
    TRANSACTION_INDEX = "transaction_index"
    # A scalar value equal to the number of Wei to be transferred to the message call’s recipient or,
    # in the case of contract creation, as an endowment to the newly created account; formally Tv.
    VALUE = "value"
    # Replay protection value based on chain_id. See EIP-155 for more info.
    V = "v"
    # The R field of the signature; the point on the curve.
    R = "r"
    # The S field of the signature; the point on the curve.
    S = "s"
    # yParity: Signature Y parity; formally Ty
    Y_PARITY = "y_parity"
    # Max Priority fee that transaction is paying. This is also known as `GasTipCap`
    MAX_PRIORITY_FEE_PER_GAS = "max_priority_fee_per_gas"
    # A scalar value equal to the maximum. This is also known as `GasFeeCap`
    MAX_FEE_PER_GAS = "max_fee_per_gas"
    # Added as EIP-pub 155: Simple replay attack protection
    CHAIN_ID = "chain_id"
    # The accessList specifies a list of addresses and storage keys;
    # these addresses and storage keys are added into the `accessed_addresses`
    # and `accessed_storage_keys` global sets (introduced in EIP-2929).
    # A gas cost is charged, though at a discount relative to the cost of accessing outside the list.
    ACCESS_LIST = "access_list"
    # Max fee per data gas aka BlobFeeCap or blobGasFeeCap
    MAX_FEE_PER_BLOB_GAS = "max_fee_per_blob_gas"
    # It contains a list of fixed size hash(32 bytes)
    BLOB_VERSIONED_HASHES = "blob_versioned_hashes"
    # The total amount of gas used in the block until this transaction was executed.
    CUMULATIVE_GAS_USED = "cumulative_gas_used"
    # The sum of the base fee and tip paid per unit of gas.
    EFFECTIVE_GAS_PRICE = "effective_gas_price"
    # Gas used by transaction
    GAS_USED = "gas_used"
    # Address of created contract if transaction was a contract creation
    CONTRACT_ADDRESS = "contract_address"
    # Bloom filter for logs produced by this transaction
    LOGS_BLOOM = "logs_bloom"
    # Transaction type. For ethereum: Legacy, Eip2930, Eip1559, Eip4844
    KIND = "type"
    # The Keccak 256-bit hash of the root node of the trie structure populated with each
    # transaction in the transactions list portion of the block; formally Ht.
    ROOT = "root"
    # If transaction is executed successfully. This is the `statusCode`
    STATUS = "status"
    # The fee associated with a transaction on the Layer 1, it is calculated as l1GasPrice multiplied by l1GasUsed
    L1_FEE = "l1_fee"
    # The gas price for transactions on the Layer 1
    L1_GAS_PRICE = "l1_gas_price"
    # The amount of gas consumed by a transaction on the Layer 1
    L1_GAS_USED = "l1_gas_used"
    # A multiplier applied to the actual gas usage on Layer 1 to calculate the dynamic costs.
    # If set to 1, it has no impact on the L1 gas usage
    L1_FEE_SCALAR = "l1_fee_scalar"
    # Amount of gas spent on L1 calldata in units of L2 gas.
    GAS_USED_FOR_L1 = "gas_used_for_l1"


class LogField(StrEnum):
    """Log filed enum"""

    # The boolean value indicating if the event was removed from the blockchain due
    # to a chain reorganization. True if the log was removed. False if it is a valid log.
    REMOVED = "removed"
    # The integer identifying the index of the event within the block's list of events.
    LOG_INDEX = "log_index"
    # The integer index of the transaction within the block's list of transactions.
    TRANSACTION_INDEX = "transaction_index"
    # The hash of the transaction that triggered the event.
    TRANSACTION_HASH = "transaction_hash"
    # The hash of the block in which the event was included.
    BLOCK_HASH = "block_hash"
    # The block number in which the event was included.
    BLOCK_NUMBER = "block_number"
    # The contract address from which the event originated.
    ADDRESS = "address"
    # The non-indexed data that was emitted along with the event.
    DATA = "data"
    # Topic pushed by contract
    TOPIC0 = "topic0"
    # Topic pushed by contract
    TOPIC1 = "topic1"
    # Topic pushed by contract
    TOPIC2 = "topic2"
    # Topic pushed by contract
    TOPIC3 = "topic3"


class TraceField(StrEnum):
    """Trace field enum"""

    # The address of the sender who initiated the transaction.
    FROM = "from"
    # The address of the recipient of the transaction if it was a transaction to an address.
    # For contract creation transactions, this field is None.
    TO = "to"
    # The type of trace, `call` or `delegatecall`, two ways to invoke a function in a smart contract.
    # `call` creates a new environment for the function to work in, so changes made in that
    # function won't affect the environment where the function was called.
    # `delegatecall` doesn't create a new environment. Instead, it runs the function within the
    # environment of the caller, so changes made in that function will affect the caller's environment.
    CALL_TYPE = "call_type"
    # The units of gas included in the transaction by the sender.
    GAS = "gas"
    # The optional input data sent with the transaction, usually used to interact with smart contracts.
    INPUT = "input"
    # The init code.
    INIT = "init"
    # The value of the native token transferred along with the transaction, in Wei.
    VALUE = "value"
    # The address of the receiver for reward transaction.
    AUTHOR = "author"
    # Kind of reward. `Block` reward or `Uncle` reward.
    REWARD_TYPE = "reward_type"
    # The hash of the block in which the transaction was included.
    BLOCK_HASH = "block_hash"
    # The number of the block in which the transaction was included.
    BLOCK_NUMBER = "block_number"
    # Destroyed address.
    ADDRESS = "address"
    # Contract code.
    CODE = "code"
    # The total used gas by the call, encoded as hexadecimal.
    GAS_USED = "gas_used"
    # The return value of the call, encoded as a hexadecimal string.
    OUTPUT = "output"
    # The number of sub-traces created during execution. When a transaction is executed on the EVM,
    # it may trigger additional sub-executions, such as when a smart contract calls another smart
    # contract or when an external account is accessed.
    SUBTRACES = "subtraces"
    # An array that indicates the position of the transaction in the trace.
    TRACE_ADDRESS = "trace_address"
    # The hash of the transaction.
    TRANSACTION_HASH = "transaction_hash"
    # The index of the transaction in the block.
    TRANSACTION_POSITION = "transaction_position"
    # The type of action taken by the transaction, `call`, `create`, `reward` and `suicide`.
    # `call` is the most common type of trace and occurs when a smart contract invokes another contract's function.
    # `create` represents the creation of a new smart contract. This type of trace occurs when a smart contract
    # is deployed to the blockchain.
    TYPE = "type"
    # A string that indicates whether the transaction was successful or not.
    # None if successful, Reverted if not.
    ERROR = "error"


class HexOutput(StrEnum):
    # Binary column won't be formatted as hex
    NO_ENCODE = "NoEncode"
    # Binary column would be formatted as prefixed hex i.e. 0xdeadbeef
    PREFIXED = "Prefixed"
    # Binary column would be formatted as non prefixed hex i.e. deadbeef
    NON_PREFIXED = "NonPrefixed"


@dataclass
class BlockSelection:
    # Hash of a block, any blocks that have one of these hashes will be returned.
    # Empty means match all.
    hash: Optional[list[str]] = None
    # Miner address of a block, any blocks that have one of these miners will be returned.
    # Empty means match all.
    miner: Optional[list[str]] = None


@dataclass
class LogSelection:
    # Address of the contract, any logs that has any of these addresses will be returned.  Empty means match all.
    address: Optional[list[str]] = None
    # Topics to match, each member of the top level array is another array, if the nth topic matches any topic specified in nth element of topics, the log will be returned. Empty means match all.
    topics: Optional[list[list[str]]] = None


@dataclass
class TransactionSelection:
    # Address the transaction should originate from. If transaction.from matches any of these, the transaction
    # will be returned. Keep in mind that this has an and relationship with to filter, so each transaction should
    # match both of them. Empty means match all.
    from_: Optional[list[str]] = None
    # Address the transaction should go to. If transaction.to matches any of these, the transaction will
    # be returned. Keep in mind that this has an and relationship with from filter, so each transaction should
    # match both of them. Empty means match all.
    to: Optional[list[str]] = None
    # If first 4 bytes of transaction input matches any of these, transaction will be returned. Empty means match all.
    sighash: Optional[list[str]] = None
    # If transaction.status matches this value, the transaction will be returned.
    status: Optional[int] = None
    # If transaction.type matches any of these values, the transaction will be returned
    kind: Optional[list[str]] = None
    # If transaction.contract_address matches any of these values, the transaction will be returned.
    contract_address: Optional[list[str]] = None
    # If transaction.hash matches any of these values the transaction will be returned.
    # empty means match all.
    hash: Optional[list[str]] = None


@dataclass
class TraceSelection:
    from_: Optional[list[str]] = None
    to: Optional[list[str]] = None
    address: Optional[list[str]] = None
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


class JoinMode(StrEnum):
    DEFAULT = "Default"
    JOIN_ALL = "JoinAll"
    JOIN_NOTHING = "JoinNothing"


@dataclass
class Query:
    # The block to start the query from
    from_block: int
    # Field selection. The user can select which fields they are interested in, requesting less fields will improve
    # query execution time and reduce the payload size so the user should always use a minimal number of fields.
    field_selection: FieldSelection
    # The block to end the query at. If not specified, the query will go until the
    # end of data. Exclusive, the returned range will be [from_block..to_block).
    # The query will return before it reaches this target block if it hits the time limit
    # configured on the server. The user should continue their query by putting the
    # next_block field in the response into from_block field of their next query. This implements
    # pagination.
    to_block: Optional[int] = None
    # List of log selections, these have an OR relationship between them, so the query will return logs
    # that match any of these selections.
    logs: Optional[list[LogSelection]] = None
    # List of transaction selections, the query will return transactions that match any of these selections, and
    # it will return transactions that are related to the returned logs.
    transactions: Optional[list[TransactionSelection]] = None
    # List of trace selections, the query will return traces that match any of these selections and
    # it will re turn traces that are related to the returned logs.
    traces: Optional[list[TraceSelection]] = None
    # List of block selections, the query will return blocks that match any of these selections
    blocks: Optional[list[BlockSelection]] = None
    # Weather to include all blocks regardless of if they are related to a returned transaction or log. Normally
    # the server will return only the blocks that are related to the transaction or logs in the response. But if this
    # is set to true, the server will return data for all blocks in the requested range [from_block, to_block).
    include_all_blocks: Optional[bool] = None
    # Maximum number of blocks that should be returned, the server might return more blocks than this number but
    # it won't overshoot by too much.
    max_num_blocks: Optional[int] = None
    # Maximum number of transactions that should be returned, the server might return more transactions than this
    # number but it won't overshoot by too much.
    max_num_transactions: Optional[int] = None
    # Maximum number of logs that should be returned, the server might return more logs than this number but
    # it won't overshoot by too much.
    max_num_logs: Optional[int] = None
    # Maximum number of traces that should be returned, the server might return more traces than this number but
    # it won't overshoot by too much.
    max_num_traces: Optional[int] = None
    # Selects join mode for the query,
    # Default: join in this order logs -> transactions -> traces -> blocks
    # JoinAll: join everything to everything. For example if logSelection matches log0, we get the
    # associated transaction of log0 and then we get associated logs of that transaction as well. Applites similarly
    # to blocks, traces.
    # JoinNothing: join nothing.
    join_mode: Optional[JoinMode] = None


@dataclass
class ColumnMapping:
    """Column mapping for stream function output. It lets you map columns you want into the DataTypes you want."""

    # Mapping for block data.
    block: Optional[Dict[BlockField, DataType]] = None
    # Mapping for transaction data.
    transaction: Optional[Dict[TransactionField, DataType]] = None
    # Mapping for log data.
    log: Optional[Dict[LogField, DataType]] = None
    # Mapping for trace data.
    trace: Optional[Dict[TraceField, DataType]] = None
    # Mapping for decoded log data.
    decoded_log: Optional[Dict[str, DataType]] = None


@dataclass
class StreamConfig:
    """Config for hypersync event streaming."""

    # Column mapping for stream function output.
    # It lets you map columns you want into the DataTypes you want.
    column_mapping: Optional[ColumnMapping] = None
    # Event signature used to populate decode logs. Decode logs would be empty if set to None.
    event_signature: Optional[str] = None
    # Determines formatting of binary columns numbers into utf8 hex.
    hex_output: Optional[HexOutput] = None
    # Maximum batch size that could be used during dynamic adjustment.
    batch_size: Optional[int] = None
    # Number of async threads that would be spawned to execute different block ranges of queries.
    concurrency: Optional[int] = None
    # Max number of blocks to fetch in a single request.
    max_num_blocks: Optional[int] = None
    # Max number of transactions to fetch in a single request.
    max_num_transactions: Optional[int] = None
    # Max number of logs to fetch in a single request.
    max_num_logs: Optional[int] = None
    # Max number of traces to fetch in a single request.
    max_num_traces: Optional[int] = None


@dataclass
class ClientConfig:
    """Configuration for the hypersync client."""

    # HyperSync server URL.
    url: Optional[str] = None
    # HyperSync server bearer token.
    bearer_token: Optional[str] = None
    # Milliseconds to wait for a response before timing out.
    http_req_timeout_millis: Optional[int] = None
    # Number of retries to attempt before returning error.
    max_num_retries: Optional[int] = None
    # Milliseconds that would be used for retry backoff increasing.
    retry_backoff_ms: Optional[int] = None
    # Initial wait time for request backoff.
    retry_base_ms: Optional[int] = None
    # Ceiling time for request backoff.
    retry_ceiling_ms: Optional[int] = None


class QueryResponseData(object):
    blocks: list[Block]
    transactions: list[Transaction]
    logs: list[Log]
    traces: list[Trace]


class RollbackGuard(object):
    # Block number of the last scanned block
    block_number: int
    # Block timestamp of the last scanned block
    timestamp: int
    # Block hash of the last scanned block
    hash: str
    # Block number of the first scanned block in memory.
    #
    # This might not be the first scanned block. It only includes blocks that are in memory (possible to be rolled back).
    first_block_number: int
    # Parent hash of the first scanned block in memory.
    #
    # This might not be the first scanned block. It only includes blocks that are in memory (possible to be rolled back).
    first_parent_hash: str


class QueryResponse(object):
    # Current height of the source hypersync instance
    archive_height: Optional[int]
    # Next block to query for, the responses are paginated so,
    #  the caller should continue the query from this block if they
    #  didn't get responses up to the to_block they specified in the Query.
    next_block: int
    # Total time it took the hypersync instance to execute the query.
    total_execution_time: int
    # Response data
    data: QueryResponseData
    # Rollback guard, supposed to be used to detect rollbacks
    rollback_guard: Optional[RollbackGuard]


class EventResponse(object):
    # Current height of the source hypersync instance
    archive_height: Optional[int]
    # Next block to query for, the responses are paginated so,
    #  the caller should continue the query from this block if they
    #  didn't get responses up to the to_block they specified in the Query.
    next_block: int
    # Total time it took the hypersync instance to execute the query.
    total_execution_time: int
    # Response data
    data: list[Event]
    # Rollback guard, supposed to be used to detect rollbacks
    rollback_guard: Optional[RollbackGuard]


class ArrowResponseData(object):
    # pyarrow.Table
    blocks: any
    # pyarrow.Table
    transactions: any
    # pyarrow.Table
    logs: any
    # pyarrow.Table
    traces: any
    # pyarrow.Table
    decoded_logs: any


class ArrowResponse(object):
    # Current height of the source hypersync instance
    archive_height: Optional[int]
    # Next block to query for, the responses are paginated so,
    #  the caller should continue the query from this block if they
    #  didn't get responses up to the to_block they specified in the Query.
    next_block: int
    # Total time it took the hypersync instance to execute the query.
    total_execution_time: int
    # Response data
    data: ArrowResponseData
    # Rollback guard, supposed to be used to detect rollbacks
    rollback_guard: Optional[RollbackGuard]


class ArrowStream(object):
    inner: _ArrowStream

    # receive the next response, returns None if the stream is finished
    async def recv(self) -> Optional[ArrowResponse]:
        await self.inner.recv()

    # close the stream so it doesn't keep loading data in the background
    async def close(self):
        await self.inner.close()


class EventStream(object):
    inner: _EventStream

    # receive the next response, returns None if the stream is finished
    async def recv(self) -> Optional[EventResponse]:
        await self.inner.recv()

    # close the stream so it doesn't keep loading data in the background
    async def close(self):
        await self.inner.close()


class QueryResponseStream(object):
    inner: _QueryResponseStream

    # receive the next response, returns None if the stream is finished
    async def recv(self) -> Optional[QueryResponse]:
        await self.inner.recv()

    # close the stream so it doesn't keep loading data in the background
    async def close(self):
        await self.inner.close()


class HypersyncClient:
    """Internal client to handle http requests and retries."""

    def __init__(self, config: ClientConfig):
        """Creates a new client with the given configuration."""
        self.inner = _HypersyncClient(asdict(config))

    async def get_height(self) -> int:
        """Get the height of the hypersync server with retries."""
        return await self.inner.get_height()

    async def get_chain_id(self) -> int:
        """Get the chain_id of the hypersync server with retries."""
        return await self.inner.get_chain_id()

    async def collect(self, query: Query, config: StreamConfig) -> QueryResponse:
        """
        Retrieves blocks, transactions, traces, and logs through a stream using the provided
        query and stream configuration.

        Implementation:
        Runs multiple queries simultaneously based on config.concurrency.
        Each query runs until it reaches query.to, server height, any max_num_* query param,
        or execution timed out by server.
        """
        return await self.inner.collect(asdict(query), asdict(config))

    async def collect_events(self, query: Query, config: StreamConfig) -> EventResponse:
        """Retrieves events through a stream using the provided query and stream configuration."""
        return await self.inner.collect_events(asdict(query), asdict(config))

    async def collect_arrow(self, query: Query, config: StreamConfig) -> ArrowResponse:
        """
        Retrieves blocks, transactions, traces, and logs in Arrow format through a stream using
        the provided query and stream configuration.
        """
        return await self.inner.collect_arrow(asdict(query), asdict(config))

    async def collect_parquet(
        self, path: str, query: Query, config: StreamConfig
    ) -> None:
        """
        Writes parquet file getting data through a stream using the provided path, query,
        and stream configuration.
        """
        return await self.inner.collect_parquet(path, asdict(query), asdict(config))

    async def get(self, query: Query) -> QueryResponse:
        """Executes query with retries and returns the response."""
        return await self.inner.get(asdict(query))

    async def get_events(self, query: Query) -> EventResponse:
        """
        Add block, transaction and log fields selection to the query, executes it with retries
        and returns the response.
        """
        return await self.inner.get_events(asdict(query))

    async def get_arrow(self, query: Query) -> ArrowResponse:
        """Executes query with retries and returns the response in Arrow format."""
        return await self.inner.get_arrow(asdict(query))

    async def stream(self, query: Query, config: StreamConfig) -> QueryResponseStream:
        """Spawns task to execute query and return data via a channel."""
        return await self.inner.stream(asdict(query), asdict(config))

    async def stream_events(self, query: Query, config: StreamConfig) -> EventStream:
        """
        Add block, transaction and log fields selection to the query and spawns task to execute it,
        returning data via a channel.
        """
        return await self.inner.stream_events(asdict(query), asdict(config))

    async def stream_arrow(self, query: Query, config: StreamConfig) -> ArrowStream:
        """Spawns task to execute query and return data via a channel in Arrow format."""
        return await self.inner.stream_arrow(asdict(query), asdict(config))


def preset_query_blocks_and_transactions(
    from_block: int, to_block: Optional[int] = None
) -> Query:
    """
    Returns a query for all Blocks and Transactions within the block range (from_block, to_block]
    If to_block is None then query runs to the head of the chain.
    Note: this is only for quickstart purposes.  For the best performance, create a custom query
    that only includes the fields you'll use in `field_selection`.
    """
    return Query(
        from_block=from_block,
        to_block=to_block,
        include_all_blocks=True,
        transactions=[TransactionSelection()],
        field_selection=FieldSelection(
            block=[e.value for e in BlockField],
            transaction=[e.value for e in TransactionField],
        ),
    )


def preset_query_blocks_and_transaction_hashes(
    from_block: int, to_block: Optional[int] = None
) -> Query:
    """
    Returns a query object for all Blocks and hashes of the Transactions within the block range
    (from_block, to_block].  Also returns the block_hash and block_number fields on each Transaction
    so it can be mapped to a block.  If to_block is None then query runs to the head of the chain.
    Note: this is only for quickstart purposes.  For the best performance, create a custom query
    that only includes the fields you'll use in `field_selection`.
    """
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
        ),
    )


def preset_query_logs(
    address: str, from_block: int, to_block: Optional[int] = None
) -> Query:
    """
    Returns a query object for all Logs within the block range (from_block, to_block] from
    the given address.  If to_block is None then query runs to the head of the chain.
    Note: this is only for quickstart purposes.  For the best performance, create a custom query
    that only includes the fields you'll use in `field_selection`.
    """
    return Query(
        from_block=from_block,
        to_block=to_block,
        logs=[LogSelection(address=[address])],
        field_selection=FieldSelection(log=[e.value for e in LogField]),
    )


def preset_query_logs_of_event(
    address: str, topic0: str, from_block: int, to_block: Optional[int] = None
) -> Query:
    """
    Returns a query for all Logs within the block range (from_block, to_block] from the
    given address with a matching topic0 event signature.  Topic0 is the keccak256 hash
    of the event signature.  If to_block is None then query runs to the head of the chain.
    Note: this is only for quickstart purposes.  For the best performance, create a custom query
    that only includes the fields you'll use in `field_selection`.
    """
    return Query(
        from_block=from_block,
        to_block=to_block,
        logs=[LogSelection(address=[address], topics=[[topic0]])],
        field_selection=FieldSelection(log=[e.value for e in LogField]),
    )
