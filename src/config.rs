use std::collections::HashMap;

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};

#[derive(
    Default, Clone, Serialize, Deserialize, dict_derive::FromPyObject, dict_derive::IntoPyObject,
)]
pub struct StreamConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub column_mapping: Option<ColumnMapping>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub event_signature: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub hex_output: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub batch_size: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_batch_size: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub min_batch_size: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub concurrency: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_num_blocks: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_num_transactions: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_num_logs: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_num_traces: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub response_bytes_ceiling: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub response_bytes_floor: Option<i64>,
}

#[derive(
    Default, Clone, Serialize, Deserialize, dict_derive::FromPyObject, dict_derive::IntoPyObject,
)]
pub struct ColumnMapping {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub block: Option<HashMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub transaction: Option<HashMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub log: Option<HashMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub trace: Option<HashMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub decoded_log: Option<HashMap<String, String>>,
}

impl StreamConfig {
    pub fn try_convert(&self) -> Result<hypersync_client::StreamConfig> {
        let json = serde_json::to_vec(self).context("serialize to json")?;
        serde_json::from_slice(&json).context("parse json")
    }
}

#[derive(
    Default, Clone, Serialize, Deserialize, dict_derive::FromPyObject, dict_derive::IntoPyObject,
)]
pub struct ClientConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bearer_token: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub http_req_timeout_millis: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_num_retries: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub retry_backoff_ms: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub retry_base_ms: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub retry_ceiling_ms: Option<i64>,
}

impl ClientConfig {
    pub fn try_convert(&self) -> Result<hypersync_client::ClientConfig> {
        let json = serde_json::to_vec(self).context("serialize to json")?;
        serde_json::from_slice(&json).context("parse json")
    }
}
