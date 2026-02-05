use pyo3::prelude::*;

/// Register all constants into the module
pub fn register_constants(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // --- Policy Key ---
    m.add("POLICY_KEY_DIGEST", 0)?;
    m.add("POLICY_KEY_SEND", 1)?;

    // --- Policy Exists ---
    m.add("POLICY_EXISTS_IGNORE", 0)?;
    m.add("POLICY_EXISTS_UPDATE", 1)?;
    m.add("POLICY_EXISTS_UPDATE_ONLY", 1)?;
    m.add("POLICY_EXISTS_REPLACE", 2)?;
    m.add("POLICY_EXISTS_REPLACE_ONLY", 3)?;
    m.add("POLICY_EXISTS_CREATE_ONLY", 4)?;

    // --- Policy Gen ---
    m.add("POLICY_GEN_IGNORE", 0)?;
    m.add("POLICY_GEN_EQ", 1)?;
    m.add("POLICY_GEN_GT", 2)?;

    // --- Policy Replica ---
    m.add("POLICY_REPLICA_MASTER", 0)?;
    m.add("POLICY_REPLICA_SEQUENCE", 1)?;
    m.add("POLICY_REPLICA_PREFER_RACK", 2)?;

    // --- Policy Commit Level ---
    m.add("POLICY_COMMIT_LEVEL_ALL", 0)?;
    m.add("POLICY_COMMIT_LEVEL_MASTER", 1)?;

    // --- Policy Read Mode AP ---
    m.add("POLICY_READ_MODE_AP_ONE", 0)?;
    m.add("POLICY_READ_MODE_AP_ALL", 1)?;

    // --- TTL Constants ---
    m.add("TTL_NAMESPACE_DEFAULT", 0)?;
    m.add("TTL_NEVER_EXPIRE", -1)?;
    m.add("TTL_DONT_UPDATE", -2)?;
    m.add("TTL_CLIENT_DEFAULT", -3)?;

    // --- Auth Mode ---
    m.add("AUTH_INTERNAL", 0)?;
    m.add("AUTH_EXTERNAL", 1)?;
    m.add("AUTH_PKI", 2)?;

    // --- Operator Constants ---
    m.add("OPERATOR_READ", 1)?;
    m.add("OPERATOR_WRITE", 2)?;
    m.add("OPERATOR_INCR", 5)?;
    m.add("OPERATOR_APPEND", 9)?;
    m.add("OPERATOR_PREPEND", 10)?;
    m.add("OPERATOR_TOUCH", 11)?;
    m.add("OPERATOR_DELETE", 12)?;

    // --- Index Type ---
    m.add("INDEX_NUMERIC", 0)?;
    m.add("INDEX_STRING", 1)?;
    m.add("INDEX_BLOB", 2)?;
    m.add("INDEX_GEO2DSPHERE", 3)?;

    // --- Index Collection Type ---
    m.add("INDEX_TYPE_DEFAULT", 0)?;
    m.add("INDEX_TYPE_LIST", 1)?;
    m.add("INDEX_TYPE_MAPKEYS", 2)?;
    m.add("INDEX_TYPE_MAPVALUES", 3)?;

    // --- Log Level ---
    m.add("LOG_LEVEL_OFF", -1)?;
    m.add("LOG_LEVEL_ERROR", 0)?;
    m.add("LOG_LEVEL_WARN", 1)?;
    m.add("LOG_LEVEL_INFO", 2)?;
    m.add("LOG_LEVEL_DEBUG", 3)?;
    m.add("LOG_LEVEL_TRACE", 4)?;

    // --- Serializer ---
    m.add("SERIALIZER_NONE", 0)?;
    m.add("SERIALIZER_PYTHON", 1)?;
    m.add("SERIALIZER_USER", 2)?;

    // --- List Return Type ---
    m.add("LIST_RETURN_NONE", 0)?;
    m.add("LIST_RETURN_INDEX", 1)?;
    m.add("LIST_RETURN_REVERSE_INDEX", 2)?;
    m.add("LIST_RETURN_RANK", 3)?;
    m.add("LIST_RETURN_REVERSE_RANK", 4)?;
    m.add("LIST_RETURN_COUNT", 5)?;
    m.add("LIST_RETURN_VALUE", 7)?;
    m.add("LIST_RETURN_EXISTS", 13)?;

    // --- List Order ---
    m.add("LIST_UNORDERED", 0)?;
    m.add("LIST_ORDERED", 1)?;

    // --- List Sort Flags ---
    m.add("LIST_SORT_DEFAULT", 0)?;
    m.add("LIST_SORT_DROP_DUPLICATES", 2)?;

    // --- List Write Flags ---
    m.add("LIST_WRITE_DEFAULT", 0)?;
    m.add("LIST_WRITE_ADD_UNIQUE", 1)?;
    m.add("LIST_WRITE_INSERT_BOUNDED", 2)?;
    m.add("LIST_WRITE_NO_FAIL", 4)?;
    m.add("LIST_WRITE_PARTIAL", 8)?;

    // --- Map Return Type ---
    m.add("MAP_RETURN_NONE", 0)?;
    m.add("MAP_RETURN_INDEX", 1)?;
    m.add("MAP_RETURN_REVERSE_INDEX", 2)?;
    m.add("MAP_RETURN_RANK", 3)?;
    m.add("MAP_RETURN_REVERSE_RANK", 4)?;
    m.add("MAP_RETURN_COUNT", 5)?;
    m.add("MAP_RETURN_KEY", 6)?;
    m.add("MAP_RETURN_VALUE", 7)?;
    m.add("MAP_RETURN_KEY_VALUE", 8)?;
    m.add("MAP_RETURN_EXISTS", 13)?;

    // --- Map Order ---
    m.add("MAP_UNORDERED", 0)?;
    m.add("MAP_KEY_ORDERED", 1)?;
    m.add("MAP_KEY_VALUE_ORDERED", 3)?;

    // --- Map Write Mode ---
    m.add("MAP_WRITE_FLAGS_DEFAULT", 0)?;
    m.add("MAP_WRITE_FLAGS_CREATE_ONLY", 1)?;
    m.add("MAP_WRITE_FLAGS_UPDATE_ONLY", 2)?;
    m.add("MAP_WRITE_FLAGS_NO_FAIL", 4)?;
    m.add("MAP_WRITE_FLAGS_PARTIAL", 8)?;

    // --- Map Write Flags (legacy names) ---
    m.add("MAP_UPDATE", 0)?;
    m.add("MAP_UPDATE_ONLY", 2)?;
    m.add("MAP_CREATE_ONLY", 1)?;

    // --- Bit Write Flags ---
    m.add("BIT_WRITE_DEFAULT", 0)?;
    m.add("BIT_WRITE_CREATE_ONLY", 1)?;
    m.add("BIT_WRITE_UPDATE_ONLY", 2)?;
    m.add("BIT_WRITE_NO_FAIL", 4)?;
    m.add("BIT_WRITE_PARTIAL", 8)?;

    // --- HLL Write Flags ---
    m.add("HLL_WRITE_DEFAULT", 0)?;
    m.add("HLL_WRITE_CREATE_ONLY", 1)?;
    m.add("HLL_WRITE_UPDATE_ONLY", 2)?;
    m.add("HLL_WRITE_NO_FAIL", 4)?;
    m.add("HLL_WRITE_ALLOW_FOLD", 8)?;

    // --- Privilege codes ---
    m.add("PRIV_READ", 10)?;
    m.add("PRIV_WRITE", 13)?;
    m.add("PRIV_READ_WRITE", 11)?;
    m.add("PRIV_READ_WRITE_UDF", 12)?;
    m.add("PRIV_USER_ADMIN", 0)?;
    m.add("PRIV_SYS_ADMIN", 1)?;
    m.add("PRIV_DATA_ADMIN", 2)?;
    m.add("PRIV_UDF_ADMIN", 3)?;
    m.add("PRIV_SINDEX_ADMIN", 4)?;
    m.add("PRIV_TRUNCATE", 14)?;

    // --- Result / Status codes ---
    m.add("AEROSPIKE_OK", 0)?;
    m.add("AEROSPIKE_ERR_SERVER", 1)?;
    m.add("AEROSPIKE_ERR_RECORD_NOT_FOUND", 2)?;
    m.add("AEROSPIKE_ERR_RECORD_GENERATION", 3)?;
    m.add("AEROSPIKE_ERR_PARAM", 4)?;
    m.add("AEROSPIKE_ERR_RECORD_EXISTS", 5)?;
    m.add("AEROSPIKE_ERR_BIN_EXISTS", 6)?;
    m.add("AEROSPIKE_ERR_CLUSTER_KEY_MISMATCH", 7)?;
    m.add("AEROSPIKE_ERR_SERVER_MEM", 8)?;
    m.add("AEROSPIKE_ERR_TIMEOUT", 9)?;
    m.add("AEROSPIKE_ERR_ALWAYS_FORBIDDEN", 10)?;
    m.add("AEROSPIKE_ERR_PARTITION_UNAVAILABLE", 11)?;
    m.add("AEROSPIKE_ERR_BIN_TYPE", 12)?;
    m.add("AEROSPIKE_ERR_RECORD_TOO_BIG", 13)?;
    m.add("AEROSPIKE_ERR_KEY_BUSY", 14)?;
    m.add("AEROSPIKE_ERR_SCAN_ABORT", 15)?;
    m.add("AEROSPIKE_ERR_UNSUPPORTED_FEATURE", 16)?;
    m.add("AEROSPIKE_ERR_BIN_NOT_FOUND", 17)?;
    m.add("AEROSPIKE_ERR_DEVICE_OVERLOAD", 18)?;
    m.add("AEROSPIKE_ERR_KEY_MISMATCH", 19)?;
    m.add("AEROSPIKE_ERR_INVALID_NAMESPACE", 20)?;
    m.add("AEROSPIKE_ERR_BIN_NAME", 21)?;
    m.add("AEROSPIKE_ERR_FAIL_FORBIDDEN", 22)?;
    m.add("AEROSPIKE_ERR_ELEMENT_NOT_FOUND", 23)?;
    m.add("AEROSPIKE_ERR_ELEMENT_EXISTS", 24)?;
    m.add("AEROSPIKE_ERR_ENTERPRISE_ONLY", 25)?;
    m.add("AEROSPIKE_ERR_OP_NOT_APPLICABLE", 26)?;
    m.add("AEROSPIKE_ERR_FILTERED_OUT", 27)?;
    m.add("AEROSPIKE_ERR_LOST_CONFLICT", 28)?;
    m.add("AEROSPIKE_QUERY_END", 50)?;
    m.add("AEROSPIKE_SECURITY_NOT_SUPPORTED", 51)?;
    m.add("AEROSPIKE_SECURITY_NOT_ENABLED", 52)?;
    m.add("AEROSPIKE_ERR_INVALID_USER", 60)?;
    m.add("AEROSPIKE_ERR_NOT_AUTHENTICATED", 80)?;
    m.add("AEROSPIKE_ERR_ROLE_VIOLATION", 81)?;
    m.add("AEROSPIKE_ERR_UDF", 100)?;
    m.add("AEROSPIKE_ERR_BATCH_DISABLED", 150)?;
    m.add("AEROSPIKE_ERR_INDEX_FOUND", 200)?;
    m.add("AEROSPIKE_ERR_INDEX_NOT_FOUND", 201)?;
    m.add("AEROSPIKE_ERR_QUERY_ABORTED", 210)?;

    // --- Client error codes (negative) ---
    m.add("AEROSPIKE_ERR_CLIENT", -1)?;
    m.add("AEROSPIKE_ERR_CONNECTION", -10)?;
    m.add("AEROSPIKE_ERR_CLUSTER", -11)?;
    m.add("AEROSPIKE_ERR_INVALID_HOST", -4)?;
    m.add("AEROSPIKE_ERR_NO_MORE_CONNECTIONS", -7)?;

    Ok(())
}
