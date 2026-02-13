"""Shared constants used across routers."""

import aerospike_py

# Desktop Manager always stores the original PK so it can be displayed on read/scan.
SEND_KEY_POLICY = {"key": aerospike_py.POLICY_KEY_SEND}
