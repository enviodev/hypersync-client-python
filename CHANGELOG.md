# Changelog

## [0.10.0] - 2026-03-14

### Upgrade to hypersync-client-rust v1.0.2

This release upgrades the underlying Rust client from v0.17 to v1.0.2, bringing
DNS failover fixes, the arrow-rs migration, new blockchain data fields, and
multiple API improvements.

### DNS Failover Fix (Critical)

- **Fixed**: Connection pools during continuous polling now refresh DNS lookups
  every 60 seconds. Previously, connection pools would remain active indefinitely
  during long-running polling sessions, causing connections to never timeout and
  DNS lookups to never re-execute. This was problematic when underlying server IP
  addresses changed during failovers on HyperSync servers.
- **Added**: HTTP/2 support via the `http2` feature in reqwest.
- **Improved**: Removed unnecessary `content-type: application/x-capnp` headers.

### Breaking Changes

#### `ClientConfig.bearer_token` renamed to `api_token`

The `bearer_token` field has been renamed to `api_token` throughout the API.

```python
# Old (deprecated, still works for backward compatibility)
config = hypersync.ClientConfig(
    url="https://eth.hypersync.xyz",
    bearer_token="your-token"
)

# New (preferred)
config = hypersync.ClientConfig(
    url="https://eth.hypersync.xyz",
    api_token="your-token"
)
```

**Note**: `bearer_token` is still accepted for backward compatibility but is
deprecated and will be removed in a future release.

#### Arrow FFI Migration: polars-arrow to arrow-rs

The Arrow integration has been migrated from `polars-arrow` (v0.42) to
`arrow-rs` (v57). This change affects the internal Arrow FFI mechanism used to
pass data between Rust and Python. From the Python user's perspective, the
pyarrow `Table` objects returned by `collect_arrow`, `get_arrow`, and
`stream_arrow` remain the same.

#### alloy Dependencies Updated: 0.8 to 1.1

The `alloy-dyn-abi`, `alloy-json-abi`, and `alloy-primitives` crates have been
updated from version 0.8 to 1.1. This should not affect Python users directly.

### New Features

#### New Transaction Fields

The following fields are now available on `Transaction` objects and in
`TransactionField` for field selection:

| Field | Type | Description |
|-------|------|-------------|
| `blob_gas_price` | `Optional[str]` | Gas price for blob transactions |
| `blob_gas_used` | `Optional[str]` | Amount of blob gas used |
| `deposit_nonce` | `Optional[str]` | Deposit transaction nonce (Optimism) |
| `deposit_receipt_version` | `Optional[str]` | Deposit receipt version (Optimism) |
| `l1_base_fee_scalar` | `Optional[str]` | Base fee scalar for L1 cost calculation |
| `l1_blob_base_fee` | `Optional[str]` | L1 blob base fee for cost calculation |
| `l1_blob_base_fee_scalar` | `Optional[str]` | L1 blob base fee scalar |
| `l1_block_number` | `Optional[str]` | L1 block number associated with tx |
| `mint` | `Optional[str]` | Amount of ETH minted (Optimism) |
| `sighash` | `Optional[str]` | 4-byte function signature hash |
| `source_hash` | `Optional[str]` | Source hash (Optimism) |

#### New Trace Fields

The following fields are now available on `Trace` objects and in `TraceField`
for field selection:

| Field | Type | Description |
|-------|------|-------------|
| `sighash` | `Optional[str]` | 4-byte function signature hash |
| `action_address` | `Optional[str]` | Action address for contract creation traces |
| `balance` | `Optional[str]` | Balance for the trace operation |
| `refund_address` | `Optional[str]` | Refund address for refund operations |

#### New DataType Enum Values

Two new column mapping data types are available:

- `DataType.DECIMAL256` - 256-bit decimal type
- `DataType.DECIMAL128` - 128-bit decimal type

#### StreamConfig.reverse

A new `reverse` field has been added to `StreamConfig` to support streaming data
in reverse chronological order:

```python
config = hypersync.StreamConfig(reverse=True)
```

### Bug Fixes

- **Fixed**: `Block.send_count`, `Block.send_root`, and `Block.mix_hash` now
  correctly map to their respective fields. Previously, they were all incorrectly
  mapped to `transactions_root`.

### Not Yet Implemented

The following features are available in the Rust client (hypersync-client-rust)
but have not yet been exposed in the Python client:

- **Height subscriptions via SSE** - Real-time block height notifications using
  Server-Sent Events.
- **Cached query bodies** - Query body caching for improved performance on
  repeated queries.

These features are planned for upcoming Python client releases.

### Internal Changes

- Bumped package version from 0.9.0 to 0.10.0.
- Updated hypersync-client dependency from 0.17 to 1.0.2.
- Migrated Arrow FFI from polars-arrow to arrow-rs v57.
- Updated alloy crates from 0.8 to 1.1.
- EventResponse data is now a flat `Vec<Event>` instead of `Vec<Vec<Event>>`.
- The Rust client now internally wraps `Client` in `Arc`, making the outer Arc
  in the Python binding redundant but harmless.
