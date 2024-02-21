use std::collections::BTreeMap;

use anyhow::{Context, Result};
use serde::Serialize;

#[derive(Default, Clone, Serialize, dict_derive::FromPyObject)]
pub struct ParquetConfig {
    /// Path to write parquet files to
    pub path: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    /// Convert binary output columns to hex
    pub hex_output: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    /// Block range size to use when making individual requests.
    pub batch_size: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    /// Controls the number of concurrent requests made to hypersync server.
    pub concurrency: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    /// Requests are retried forever internally if this param is set to true.
    pub retry: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    /// Define type mapping for output columns
    pub column_mapping: Option<ColumnMapping>,
    #[serde(skip_serializing_if = "Option::is_none")]
    /// Define type mapping for output columns
    pub event_signature: Option<String>,
}

#[derive(Default, Clone, Serialize, dict_derive::FromPyObject)]
pub struct ColumnMapping {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub block: Option<BTreeMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub transaction: Option<BTreeMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub log: Option<BTreeMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub trace: Option<BTreeMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub decoded_log: Option<BTreeMap<String, String>>,
}

impl ParquetConfig {
    pub fn try_convert(&self) -> Result<skar_client::ParquetConfig> {
        let json = serde_json::to_vec(self).context("serialize to json")?;
        serde_json::from_slice(&json).context("parse json")
    }
}

#[derive(Default, Clone, Serialize, dict_derive::FromPyObject)]
pub struct Config {
    /// Url of the source hypersync instance
    pub url: String,
    /// Optional bearer_token to put into http requests made to source hypersync instance
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bearer_token: Option<String>,
    /// Timout treshold for a single http request in milliseconds, default is 30 seconds (30_000ms)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub http_req_timeout_millis: Option<i64>,
}

impl Config {
    pub fn try_convert(&self) -> Result<skar_client::Config> {
        let json = serde_json::to_vec(self).context("serialize to json")?;
        serde_json::from_slice(&json).context("parse json")
    }
}
