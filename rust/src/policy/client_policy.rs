use aerospike_core::{AuthMode, ClientPolicy};
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Parse a Python config dict into a ClientPolicy
pub fn parse_client_policy(config: &Bound<'_, PyDict>) -> PyResult<ClientPolicy> {
    let mut policy = ClientPolicy::default();

    // Timeout
    if let Some(timeout) = config.get_item("timeout")? {
        policy.timeout = timeout.extract::<u32>()?;
    }

    // Idle timeout
    if let Some(idle_timeout) = config.get_item("idle_timeout")? {
        policy.idle_timeout = idle_timeout.extract::<u32>()?;
    }

    // Max connections per node
    if let Some(max_conns) = config.get_item("max_conns_per_node")? {
        policy.max_conns_per_node = max_conns.extract::<usize>()?;
    }

    // Min connections per node
    if let Some(min_conns) = config.get_item("min_conns_per_node")? {
        policy.min_conns_per_node = min_conns.extract::<usize>()?;
    }

    // Tend interval
    if let Some(tend_interval) = config.get_item("tend_interval")? {
        policy.tend_interval = tend_interval.extract::<u32>()?;
    }

    // Cluster name
    if let Some(cluster_name) = config.get_item("cluster_name")? {
        if !cluster_name.is_none() {
            policy.cluster_name = Some(cluster_name.extract::<String>()?);
        }
    }

    // Use services alternate
    if let Some(use_alt) = config.get_item("use_services_alternate")? {
        policy.use_services_alternate = use_alt.extract::<bool>()?;
    }

    // Authentication: user/password
    if let Some(user) = config.get_item("user")? {
        if !user.is_none() {
            let username: String = user.extract()?;
            let password: String = config
                .get_item("password")?
                .map(|p| p.extract::<String>())
                .unwrap_or(Ok(String::new()))?;

            let auth_mode = if let Some(mode) = config.get_item("auth_mode")? {
                let mode_val: i32 = mode.extract()?;
                if mode_val == 1 {
                    AuthMode::External(username, password)
                } else {
                    AuthMode::Internal(username, password)
                }
            } else {
                AuthMode::Internal(username, password)
            };
            policy.auth_mode = auth_mode;
        }
    }

    Ok(policy)
}
