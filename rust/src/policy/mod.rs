pub mod admin_policy;
pub mod batch_policy;
pub mod client_policy;
pub mod query_policy;
pub mod read_policy;
pub mod write_policy;

/// Extract simple typed fields from a Python dict into a policy struct.
///
/// Each field's type is inferred from the assignment target.
/// Complex conversions (enum matching, expression filters) should remain inline.
macro_rules! extract_policy_fields {
    ($dict:expr, { $( $key:literal => $($target:tt).+ );* $(;)? }) => {
        $(
            if let Some(val) = $dict.get_item($key)? {
                $($target).+ = val.extract()?;
            }
        )*
    };
}

pub(crate) use extract_policy_fields;

/// Parse an optional `filter_expression` field from a Python dict.
pub fn parse_filter_expression(
    dict: &pyo3::Bound<'_, pyo3::types::PyDict>,
) -> pyo3::PyResult<Option<aerospike_core::expressions::Expression>> {
    use pyo3::types::PyDictMethods;
    if let Some(val) = dict.get_item("filter_expression")? {
        if crate::expressions::is_expression(&val) {
            return Ok(Some(crate::expressions::py_to_expression(&val)?));
        }
    }
    Ok(None)
}
