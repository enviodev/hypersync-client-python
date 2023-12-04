use std::num::NonZeroU64;

use anyhow::{Context, Result};
use pyo3::{pyclass};

#[pyclass]
#[derive(Default, Clone)]
pub struct Config {
    /// Url of the source hypersync instance
    pub url: String,
    /// Optional bearer_token to put into http requests made to source hypersync instance
    pub bearer_token: Option<String>,
    /// Timout treshold for a single http request in milliseconds, default is 30 seconds (30_000ms)
    pub http_req_timeout_millis: Option<i64>,
}

impl Config {
    pub fn new(
        url: String,
        bearer_token: Option<String>,
        http_req_timeout_millis: Option<i64>,
    ) -> Self {
        Self {
            url,
            bearer_token,
            http_req_timeout_millis,
        }
    }

    pub fn try_convert(&self) -> Result<skar_client::Config> {
        Ok(skar_client::Config {
            url: self.url.parse().context("parse url")?,
            bearer_token: self.bearer_token.clone(),
            http_req_timeout_millis: match self.http_req_timeout_millis {
                Some(c) => NonZeroU64::new(c.try_into().context("parse timeout")?)
                    .context("parse timeout")?,
                None => NonZeroU64::new(30000).unwrap(),
            },
        })
    }
}
