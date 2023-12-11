use anyhow::{Context, Result};
use serde::Serialize;

#[derive(Default, Clone, Serialize, dict_derive::FromPyObject)]
pub struct LogSelection {
    /// Address of the contract, any logs that has any of these addresses will be returned.
    /// Empty means match all.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub address: Option<Vec<String>>,
    /// Topics to match, each member of the top level array is another array, if the nth topic matches any
    ///  topic specified in topics[n] the log will be returned. Empty means match all.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub topics: Option<Vec<Vec<String>>>,
}

#[derive(Default, Clone, Serialize, dict_derive::FromPyObject)]
pub struct TransactionSelection {
    /// Address the transaction should originate from. If transaction.from matches any of these, the transaction
    ///  will be returned. Keep in mind that this has an and relationship with to filter, so each transaction should
    ///  match both of them. Empty means match all.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub from: Option<Vec<String>>,
    /// Address the transaction should go to. If transaction.to matches any of these, the transaction will
    ///  be returned. Keep in mind that this has an and relationship with from filter, so each transaction should
    ///  match both of them. Empty means match all.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub to: Option<Vec<String>>,
    /// If first 4 bytes of transaction input matches any of these, transaction will be returned. Empty means match all.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sighash: Option<Vec<String>>,
    /// If tx.status matches this it will be returned.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub status: Option<i64>,
}

#[derive(Default, Clone, Serialize, dict_derive::FromPyObject)]
pub struct FieldSelection {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub block: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub transaction: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub log: Option<Vec<String>>,
}

#[derive(Default, Clone, Serialize, dict_derive::FromPyObject)]
pub struct Query {
    /// The block to start the query from
    pub from_block: i64,
    /// The block to end the query at. If not specified, the query will go until the
    ///  end of data. Exclusive, the returned range will be [from_block..to_block).
    ///
    /// The query will return before it reaches this target block if it hits the time limit
    ///  configured on the server. The user should continue their query by putting the
    ///  next_block field in the response into from_block field of their next query. This implements
    ///  pagination.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub to_block: Option<i64>,
    /// List of log selections, these have an or relationship between them, so the query will return logs
    /// that match any of these selections.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub logs: Option<Vec<LogSelection>>,
    /// List of transaction selections, the query will return transactions that match any of these selections and
    ///  it will return transactions that are related to the returned logs.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub transactions: Option<Vec<TransactionSelection>>,
    /// Weather to include all blocks regardless of if they are related to a returned transaction or log. Normally
    ///  the server will return only the blocks that are related to the transaction or logs in the response. But if this
    ///  is set to true, the server will return data for all blocks in the requested range [from_block, to_block).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub include_all_blocks: Option<bool>,
    /// Field selection. The user can select which fields they are interested in, requesting less fields will improve
    ///  query execution time and reduce the payload size so the user should always use a minimal number of fields.
    pub field_selection: FieldSelection,
    /// Maximum number of blocks that should be returned, the server might return more blocks than this number but
    ///  it won't overshoot by too much.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_num_blocks: Option<i64>,
    /// Maximum number of transactions that should be returned, the server might return more transactions than this number but
    ///  it won't overshoot by too much.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_num_transactions: Option<i64>,
    /// Maximum number of logs that should be returned, the server might return more logs than this number but
    ///  it won't overshoot by too much.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_num_logs: Option<i64>,
}

impl Query {
    pub fn try_convert(&self) -> Result<skar_net_types::Query> {
        let json = serde_json::to_vec(self).context("serialize to json")?;
        serde_json::from_slice(&json).context("parse json")
    }
}
