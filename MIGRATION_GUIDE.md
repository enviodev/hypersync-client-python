# Migration Guide: hypersync v0.9 to v0.10

This guide covers all changes needed to migrate from hypersync-client-python
v0.9.x (backed by hypersync-client-rust v0.17) to v0.10.0 (backed by
hypersync-client-rust v1.0.2).

## Quick Summary

| Change | Action Required |
|--------|----------------|
| `bearer_token` renamed to `api_token` | **Recommended** (old name still works) |
| New Transaction/Trace fields | None (additive) |
| New DataType enum values | None (additive) |
| StreamConfig.reverse | None (additive) |
| Block field bug fixes | **Awareness** (may affect data) |
| polars-arrow to arrow-rs | No significant change, small internal changes (transparent to Python) |
| alloy 0.8 to 1.1 | None (transparent to Python) |
| DNS failover fix | None (transparent fix) |

---

## 1. ClientConfig: `bearer_token` to `api_token`

### What Changed

The `bearer_token` field in `ClientConfig` has been renamed to `api_token` to
align with the upstream Rust client terminology.

### Migration

**Before (v0.9):**
```python
import hypersync

client = hypersync.HypersyncClient(hypersync.ClientConfig(
    url="https://eth.hypersync.xyz",
    bearer_token="your-api-token"
))
```

**After (v0.10):**
```python
import hypersync

client = hypersync.HypersyncClient(hypersync.ClientConfig(
    url="https://eth.hypersync.xyz",
    api_token="your-api-token"
))
```

**Backward compatibility:** `bearer_token` is still accepted and will be
automatically mapped to `api_token`. However, it is deprecated and will be
removed in a future version. If both `api_token` and `bearer_token` are
specified, `api_token` takes precedence.

---

## 2. New Transaction Fields

The following fields have been added to the `Transaction` class and
`TransactionField` enum. These are all additive and require no migration action.

### EIP-4844 Blob Transaction Fields

```python
# New TransactionField enum values
TransactionField.BLOB_GAS_PRICE
TransactionField.BLOB_GAS_USED

# Available on Transaction objects
tx.blob_gas_price  # Optional[str] - hex encoded
tx.blob_gas_used   # Optional[str] - hex encoded
```

### Optimism / L2 Fields

```python
# New TransactionField enum values
TransactionField.DEPOSIT_NONCE
TransactionField.DEPOSIT_RECEIPT_VERSION
TransactionField.L1_BASE_FEE_SCALAR
TransactionField.L1_BLOB_BASE_FEE
TransactionField.L1_BLOB_BASE_FEE_SCALAR
TransactionField.L1_BLOCK_NUMBER
TransactionField.MINT
TransactionField.SOURCE_HASH

# Available on Transaction objects
tx.deposit_nonce             # Optional[str]
tx.deposit_receipt_version   # Optional[str]
tx.l1_base_fee_scalar        # Optional[str]
tx.l1_blob_base_fee          # Optional[str]
tx.l1_blob_base_fee_scalar   # Optional[str]
tx.l1_block_number           # Optional[str]
tx.mint                      # Optional[str]
tx.source_hash               # Optional[str]
```

### Function Signature Hash

```python
TransactionField.SIGHASH

tx.sighash  # Optional[str] - 4-byte function signature hash
```

### Usage Example

```python
query = hypersync.Query(
    from_block=19000000,
    field_selection=hypersync.FieldSelection(
        transaction=[
            hypersync.TransactionField.HASH,
            hypersync.TransactionField.FROM,
            hypersync.TransactionField.TO,
            hypersync.TransactionField.SIGHASH,          # New
            hypersync.TransactionField.BLOB_GAS_USED,    # New
        ]
    ),
    transactions=[hypersync.TransactionSelection()]
)
```

---

## 3. New Trace Fields

The following fields have been added to the `Trace` class and `TraceField` enum.

```python
# New TraceField enum values
TraceField.SIGHASH
TraceField.ACTION_ADDRESS
TraceField.BALANCE
TraceField.REFUND_ADDRESS

# Available on Trace objects
trace.sighash         # Optional[str] - 4-byte function signature hash
trace.action_address  # Optional[str] - action address for contract creation
trace.balance         # Optional[str] - balance for the trace operation
trace.refund_address  # Optional[str] - refund address for refund operations
```

---

## 4. New DataType Enum Values

Two new column mapping data types are available for use with `ColumnMapping`:

```python
hypersync.DataType.DECIMAL256  # 256-bit decimal type
hypersync.DataType.DECIMAL128  # 128-bit decimal type
```

### Usage Example

```python
config = hypersync.StreamConfig(
    column_mapping=hypersync.ColumnMapping(
        transaction={
            hypersync.TransactionField.VALUE: hypersync.DataType.DECIMAL256,
            hypersync.TransactionField.GAS_PRICE: hypersync.DataType.DECIMAL128,
        }
    )
)
```

---

## 5. StreamConfig.reverse

A new `reverse` boolean field allows streaming data in reverse chronological
order:

```python
config = hypersync.StreamConfig(
    reverse=True  # Stream from newest to oldest
)
```

---

## 6. Block Field Bug Fixes

**Impact:** If you were using `Block.send_count`, `Block.send_root`, or
`Block.mix_hash`, their values were previously incorrect (they all returned the
`transactions_root` value). They now correctly return their respective field
values from the blockchain data.

If your code relied on this incorrect behavior, you may see different values
after upgrading.

---

## 7. Features Not Yet Available in Python

The following features exist in the Rust client (hypersync-client-rust v1.0.2)
but have **not yet been implemented** in the Python client:

- **Height subscriptions via SSE** — The Rust client supports real-time block
  height notifications using Server-Sent Events. This is not yet exposed in the
  Python bindings.
- **Cached query bodies** — The Rust client supports caching query bodies for
  improved performance on repeated queries. This is not yet available in the
  Python client.

These features are planned for upcoming Python client releases.

---

## 8. Internal Changes (No Action Required)

These changes are transparent to Python users but are documented for
completeness:

### Arrow FFI Migration

The Arrow integration has been migrated from `polars-arrow` (v0.42) to
`arrow-rs` (v57). The pyarrow `Table` objects returned by `collect_arrow`,
`get_arrow`, and `stream_arrow` remain functionally identical.

### alloy Crate Updates

The Ethereum ABI encoding/decoding libraries (`alloy-dyn-abi`, `alloy-json-abi`,
`alloy-primitives`) have been updated from version 0.8 to 1.1. This does not
affect the Python API.

### EventResponse Data Flattening

The internal `EventResponse.data` structure changed from `Vec<Vec<Event>>` to
`Vec<Event>`. The Python API (`EventResponse.data`) continues to return a flat
list of `Event` objects as before, so this change is transparent.

### DNS Failover Fix

The HTTP client now recreates its connection pool every 60 seconds to ensure DNS
lookups are refreshed. This fixes an issue where long-running polling sessions
would hold stale connections to IPs that had changed during server failovers.
This is completely transparent and requires no code changes.

### Client Arc Wrapping

The Rust `Client` struct now internally wraps its state in `Arc`, making it
cheap to clone. The Python binding's outer `Arc` wrapper is redundant but
harmless and has been preserved for simplicity.

---

## Dependency Changes

### Cargo.toml (for building from source)

| Dependency | Old Version | New Version |
|-----------|-------------|-------------|
| `hypersync-client` | 0.17 | 1.0.2 |
| `polars-arrow` | 0.42 | **Removed** |
| `arrow` | — | 57 |
| `alloy-dyn-abi` | 0.8 | 1.1 |
| `alloy-json-abi` | 0.8 | 1.1 |
| `alloy-primitives` | 0.8 | 1.1 |

---

## Complete Version History (Rust Client)

The Rust client went through these versions between 0.17 and 1.0.2:

- **0.17.x** - Previous Python client dependency
- **0.18.0-0.18.5** - Incremental improvements
- **0.19.0** - Minor updates
- **0.20.0** - Release candidates and stable
- **0.21.0-0.21.2** - Incremental improvements
- **0.22.0** - Minor updates
- **0.23.0** (Dec 2025) - Pre-1.0 release
- **1.0.0** (Jan 2026) - Stability milestone, streaming large payload fixes
- **1.0.1** (Feb 2026) - DNS failover fixes, HTTP/2 support
- **1.0.2** (Mar 2026) - Latest stable release
