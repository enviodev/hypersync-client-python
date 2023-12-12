use alloy_dyn_abi::DynSolValue;
use alloy_primitives::{Signed, Uint};
use pyo3::{ffi, pyclass, IntoPy, PyObject, Python};

/// Data relating to a single event (log)
#[pyclass]
#[pyo3(get_all)]
#[derive(Default, Clone)]
pub struct Event {
    /// Transaction that triggered this event
    pub transaction: Option<Transaction>,
    /// Block that this event happened in
    pub block: Option<Block>,
    /// Evm log data
    pub log: Log,
}

/// Evm log object
///
/// See ethereum rpc spec for the meaning of fields
#[pyclass]
#[pyo3(get_all)]
#[derive(Default, Clone)]
pub struct Log {
    pub removed: Option<bool>,
    pub log_index: i64,
    pub transaction_index: i64,
    pub transaction_hash: Option<String>,
    pub block_hash: Option<String>,
    pub block_number: i64,
    pub address: Option<String>,
    pub data: Option<String>,
    pub topics: Vec<Option<String>>,
}

/// Evm transaction object
///
/// See ethereum rpc spec for the meaning of fields
#[pyclass]
#[pyo3(get_all)]
#[derive(Default, Clone)]
pub struct Transaction {
    pub block_hash: Option<String>,
    pub block_number: i64,
    pub from: Option<String>,
    pub gas: Option<String>,
    pub gas_price: Option<String>,
    pub hash: Option<String>,
    pub input: Option<String>,
    pub nonce: Option<String>,
    pub to: Option<String>,
    pub transaction_index: i64,
    pub value: Option<String>,
    pub v: Option<String>,
    pub r: Option<String>,
    pub s: Option<String>,
    pub max_priority_fee_per_gas: Option<String>,
    pub max_fee_per_gas: Option<String>,
    pub chain_id: Option<String>,
    pub cumulative_gas_used: Option<String>,
    pub effective_gas_price: Option<String>,
    pub gas_used: Option<String>,
    pub contract_address: Option<String>,
    pub logs_bloom: Option<String>,
    pub kind: Option<u32>,
    pub root: Option<String>,
    pub status: Option<u32>,
}

/// Evm block header object
///
/// See ethereum rpc spec for the meaning of fields
#[pyclass]
#[pyo3(get_all)]
#[derive(Default, Clone)]
pub struct Block {
    pub number: i64,
    pub hash: Option<String>,
    pub parent_hash: Option<String>,
    pub nonce: Option<String>,
    pub sha3_uncles: Option<String>,
    pub logs_bloom: Option<String>,
    pub transactions_root: Option<String>,
    pub state_root: Option<String>,
    pub receipts_root: Option<String>,
    pub miner: Option<String>,
    pub difficulty: Option<String>,
    pub total_difficulty: Option<String>,
    pub extra_data: Option<String>,
    pub size: Option<String>,
    pub gas_limit: Option<String>,
    pub gas_used: Option<String>,
    pub timestamp: Option<i64>,
    pub base_fee_per_gas: Option<String>,
}

/// Decoded EVM log
#[pyclass]
#[pyo3(get_all)]
#[derive(Default)]
pub struct DecodedEvent {
    pub indexed: Vec<PyObject>,
    pub body: Vec<PyObject>,
}

pub fn to_py(val: DynSolValue, py: Python) -> PyObject {
    match val {
        DynSolValue::Bool(b) => b.into_py(py),
        DynSolValue::Int(v, _) => {
            let bytes: [u8; Signed::<256, 4>::BYTES] = v.to_le_bytes();
            let ptr: *const u8 = bytes.as_ptr();
            unsafe {
                let obj = ffi::_PyLong_FromByteArray(ptr, Signed::<256, 4>::BYTES, 1, 1);
                PyObject::from_owned_ptr(py, obj)
            }
        }
        DynSolValue::Uint(v, _) => {
            //v.into_py(py)
            let bytes: [u8; Uint::<256, 4>::BYTES] = v.to_le_bytes();
            let ptr: *const u8 = bytes.as_ptr();
            unsafe {
                let obj = ffi::_PyLong_FromByteArray(ptr, Uint::<256, 4>::BYTES, 1, 0);
                PyObject::from_owned_ptr(py, obj)
            }
        }
        DynSolValue::FixedBytes(bytes, _) => prefix_hex::encode(bytes.as_slice()).into_py(py),
        DynSolValue::Address(bytes) => prefix_hex::encode(bytes.as_slice()).into_py(py),
        DynSolValue::Function(bytes) => prefix_hex::encode(bytes.as_slice()).into_py(py),
        DynSolValue::Bytes(bytes) => prefix_hex::encode(bytes.as_slice()).into_py(py),
        DynSolValue::String(bytes) => prefix_hex::encode(bytes.as_bytes()).into_py(py),
        DynSolValue::Array(vals) => vals
            .into_iter()
            .map(|a| to_py(a, py))
            .collect::<Vec<PyObject>>()
            .into_py(py),
        DynSolValue::FixedArray(vals) => vals
            .into_iter()
            .map(|a| to_py(a, py))
            .collect::<Vec<PyObject>>()
            .into_py(py),
        DynSolValue::Tuple(vals) => vals
            .into_iter()
            .map(|a| to_py(a, py))
            .collect::<Vec<PyObject>>()
            .into_py(py),
    }
}
