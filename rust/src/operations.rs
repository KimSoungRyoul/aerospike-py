use aerospike_core::{operations, operations::Operation, Bin, Value};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use crate::types::value::py_to_value;

// Operation type constants (matching Python aerospike client)
const OP_READ: i32 = 1;
const OP_WRITE: i32 = 2;
const OP_INCR: i32 = 5;
const OP_APPEND: i32 = 9;
const OP_PREPEND: i32 = 10;
const OP_TOUCH: i32 = 11;
const OP_DELETE: i32 = 12;

/// Convert a Python list of operation dicts to Rust Operations
/// Each operation is a dict: {"op": int, "bin": str, "val": any}
pub fn py_ops_to_rust(ops_list: &Bound<'_, PyList>) -> PyResult<Vec<Operation>> {
    let mut rust_ops: Vec<Operation> = Vec::with_capacity(ops_list.len());

    for item in ops_list.iter() {
        let dict = item.downcast::<PyDict>()?;

        let op_code: i32 = dict
            .get_item("op")?
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Operation must have 'op' key"))?
            .extract()?;

        let bin_name: Option<String> = dict
            .get_item("bin")?
            .and_then(|v| if v.is_none() { None } else { Some(v) })
            .map(|v| v.extract())
            .transpose()?;

        let val: Option<Value> = dict
            .get_item("val")?
            .and_then(|v| if v.is_none() { None } else { Some(v) })
            .map(|v| py_to_value(&v))
            .transpose()?;

        let op = match op_code {
            OP_READ => {
                if let Some(name) = &bin_name {
                    operations::get_bin(name)
                } else {
                    operations::get()
                }
            }
            OP_WRITE => {
                let name = bin_name.ok_or_else(|| {
                    pyo3::exceptions::PyValueError::new_err("Write operation requires 'bin'")
                })?;
                let v = val.unwrap_or(Value::Nil);
                // We need an owned Bin for the operation
                let bin = Bin::new(name, v);
                operations::put(&bin)
            }
            OP_INCR => {
                let name = bin_name.ok_or_else(|| {
                    pyo3::exceptions::PyValueError::new_err("Increment operation requires 'bin'")
                })?;
                let v = val.unwrap_or(Value::Int(1));
                let bin = Bin::new(name, v);
                operations::add(&bin)
            }
            OP_APPEND => {
                let name = bin_name.ok_or_else(|| {
                    pyo3::exceptions::PyValueError::new_err("Append operation requires 'bin'")
                })?;
                let v = val.unwrap_or(Value::String(String::new()));
                let bin = Bin::new(name, v);
                operations::append(&bin)
            }
            OP_PREPEND => {
                let name = bin_name.ok_or_else(|| {
                    pyo3::exceptions::PyValueError::new_err("Prepend operation requires 'bin'")
                })?;
                let v = val.unwrap_or(Value::String(String::new()));
                let bin = Bin::new(name, v);
                operations::prepend(&bin)
            }
            OP_TOUCH => operations::touch(),
            OP_DELETE => operations::delete(),
            _ => {
                return Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Unsupported operation code: {op_code}"
                )));
            }
        };

        rust_ops.push(op);
    }

    Ok(rust_ops)
}
