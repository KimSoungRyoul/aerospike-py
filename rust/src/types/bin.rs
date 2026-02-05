use aerospike_core::Bin;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::value::py_to_value;

/// Convert a Python dict of bins to a Vec<Bin>
pub fn py_dict_to_bins(dict: &Bound<'_, PyDict>) -> PyResult<Vec<Bin>> {
    let mut bins = Vec::with_capacity(dict.len());
    for (key, val) in dict.iter() {
        let name: String = key.extract()?;
        let value = py_to_value(&val)?;
        bins.push(Bin::new(name, value));
    }
    Ok(bins)
}
