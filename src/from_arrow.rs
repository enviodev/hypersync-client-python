use anyhow::Result;
use arrow2::array::{BinaryArray, BooleanArray, UInt64Array, UInt8Array};
use skar_client::ArrowBatch;

use crate::types::{Block, Log, Transaction};

pub trait FromArrow: Sized {
    fn from_arrow(batch: &ArrowBatch) -> Result<Vec<Self>>;
}

impl FromArrow for Log {
    fn from_arrow(batch: &ArrowBatch) -> Result<Vec<Self>> {
        let mut out: Vec<Self> = vec![Default::default(); batch.chunk.len()];

        if let Ok(col) = batch.column::<UInt64Array>("block_number") {
            for (target, &val) in out.iter_mut().zip(col.values_iter()) {
                target.block_number = val.try_into().unwrap();
            }
        }

        if let Ok(col) = batch.column::<UInt64Array>("transaction_index") {
            for (target, &val) in out.iter_mut().zip(col.values_iter()) {
                target.transaction_index = val.try_into().unwrap();
            }
        }

        if let Ok(col) = batch.column::<UInt64Array>("log_index") {
            for (target, &val) in out.iter_mut().zip(col.values_iter()) {
                target.log_index = val.try_into().unwrap();
            }
        }

        if let Ok(col) = batch.column::<BooleanArray>("removed") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.removed = val;
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("transaction_hash") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.transaction_hash = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("block_hash") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.block_hash = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("address") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.address = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("data") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.data = val.map(prefix_hex::encode);
            }
        }

        for topic_name in ["topic0", "topic1", "topic2", "topic3"] {
            if let Ok(col) = batch.column::<BinaryArray<i32>>(topic_name) {
                for (target, val) in out.iter_mut().zip(col.iter()) {
                    target.topics.push(val.map(prefix_hex::encode));
                }
            }
        }

        Ok(out)
    }
}

impl FromArrow for Transaction {
    fn from_arrow(batch: &ArrowBatch) -> Result<Vec<Self>> {
        let mut out: Vec<Self> = vec![Default::default(); batch.chunk.len()];

        if let Ok(col) = batch.column::<UInt64Array>("block_number") {
            for (target, &val) in out.iter_mut().zip(col.values_iter()) {
                target.block_number = val.try_into().unwrap();
            }
        }

        if let Ok(col) = batch.column::<UInt64Array>("transaction_index") {
            for (target, &val) in out.iter_mut().zip(col.values_iter()) {
                target.transaction_index = val.try_into().unwrap();
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("block_hash") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.block_hash = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("from") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.from = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("gas") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.gas = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("gas_price") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.gas_price = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("hash") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.hash = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("input") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.input = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("nonce") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.nonce = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("to") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.to = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("value") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.value = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("v") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.v = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("r") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.r = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("s") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.s = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("max_priority_fee_per_gas") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.max_priority_fee_per_gas = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("max_fee_per_gas") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.max_fee_per_gas = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("chain_id") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.chain_id = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("cumulative_gas_used") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.cumulative_gas_used = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("effective_gas_price") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.effective_gas_price = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("gas_used") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.gas_used = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("contract_address") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.contract_address = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("logs_bloom") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.logs_bloom = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<UInt8Array>("kind") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.kind = val.map(|&v| v.into());
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("root") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.root = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<UInt8Array>("status") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.status = val.map(|&v| v.into());
            }
        }

        Ok(out)
    }
}

impl FromArrow for Block {
    fn from_arrow(batch: &ArrowBatch) -> Result<Vec<Self>> {
        let mut out: Vec<Self> = vec![Default::default(); batch.chunk.len()];

        if let Ok(col) = batch.column::<UInt64Array>("number") {
            for (target, &val) in out.iter_mut().zip(col.values_iter()) {
                target.number = val.try_into().unwrap();
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("hash") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.hash = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("parent_hash") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.parent_hash = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("nonce") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.nonce = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("sha3_uncles") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.sha3_uncles = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("logs_bloom") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.logs_bloom = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("transactions_root") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.transactions_root = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("state_root") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.state_root = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("receipts_root") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.receipts_root = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("miner") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.miner = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("difficulty") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.difficulty = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("total_difficulty") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.total_difficulty = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("extra_data") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.extra_data = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("size") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.size = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("gas_limit") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.gas_limit = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("gas_used") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.gas_used = val.map(prefix_hex::encode);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("timestamp") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.timestamp = val.map(i64_from_bytes);
            }
        }

        if let Ok(col) = batch.column::<BinaryArray<i32>>("base_fee_per_gas") {
            for (target, val) in out.iter_mut().zip(col.iter()) {
                target.base_fee_per_gas = val.map(prefix_hex::encode);
            }
        }

        Ok(out)
    }
}

fn i64_from_bytes(v: &[u8]) -> i64 {
    assert!(v.len() <= std::mem::size_of::<i64>());
    let mut buf = [0; std::mem::size_of::<i64>()];
    buf[std::mem::size_of::<i64>() - v.len()..].copy_from_slice(v);
    i64::from_be_bytes(buf)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_i64_from_bytes() {
        let v: Vec<u8> = prefix_hex::decode("0x5bbc001f").unwrap();
        let v = i64_from_bytes(&v);

        assert_eq!(v, 1539047455);
    }
}
