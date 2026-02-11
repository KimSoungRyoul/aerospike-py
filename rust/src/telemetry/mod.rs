#[cfg(feature = "telemetry")]
pub mod logging;

use pyo3::prelude::*;

#[cfg(feature = "telemetry")]
use std::sync::Once;

#[cfg(feature = "telemetry")]
static INIT: Once = Once::new();

/// Initialize telemetry subsystem with the given log level.
/// Level mapping: -1=OFF, 0=ERROR, 1=WARN, 2=INFO, 3=DEBUG, 4=TRACE
#[pyfunction]
#[pyo3(signature = (level))]
pub fn _init_telemetry(level: i32) -> PyResult<()> {
    #[cfg(feature = "telemetry")]
    {
        if level < 0 {
            return Ok(());
        }

        let filter = match level {
            0 => "error",
            1 => "warn",
            2 => "info",
            3 => "debug",
            _ => "trace",
        };

        INIT.call_once(|| {
            // Bridge log crate -> tracing (captures aerospike-core logs)
            let _ = tracing_log::LogTracer::init();

            // Initialize the logging channel subscriber
            logging::init_subscriber(filter);
        });
    }

    #[cfg(not(feature = "telemetry"))]
    {
        let _ = level;
    }

    Ok(())
}

/// Drain buffered log messages from Rust side.
/// Returns a list of dicts: [{"level": int, "target": str, "message": str}, ...]
#[pyfunction]
pub fn _flush_logs(py: Python<'_>) -> PyResult<Vec<pyo3::Py<pyo3::types::PyDict>>> {
    #[cfg(feature = "telemetry")]
    {
        let records = logging::drain_logs();
        let mut result = Vec::with_capacity(records.len());
        for rec in records {
            let dict = pyo3::types::PyDict::new(py);
            dict.set_item("level", rec.level)?;
            dict.set_item("target", &rec.target)?;
            dict.set_item("message", &rec.message)?;
            result.push(dict.unbind());
        }
        Ok(result)
    }

    #[cfg(not(feature = "telemetry"))]
    {
        let _ = py;
        Ok(Vec::new())
    }
}

pub fn register_telemetry_functions(m: &pyo3::Bound<'_, pyo3::types::PyModule>) -> PyResult<()> {
    m.add_function(pyo3::wrap_pyfunction!(_init_telemetry, m)?)?;
    m.add_function(pyo3::wrap_pyfunction!(_flush_logs, m)?)?;
    Ok(())
}
