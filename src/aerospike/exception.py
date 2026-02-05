"""Aerospike exception hierarchy.

Re-exports all exception classes from the native Rust module.
This module provides the full exception hierarchy for compatibility
with the existing aerospike-client-python.
"""

from aerospike._aerospike import (
    # Base exceptions
    AerospikeError,
    ClientError,
    ClusterError,
    InvalidArgError,
    RecordError,
    ServerError,
    TimeoutError,
    # Record-level exceptions
    RecordNotFound,
    RecordExistsError,
    RecordGenerationError,
    RecordTooBig,
    BinNameError,
    BinExistsError,
    BinNotFound,
    BinTypeError,
    FilteredOut,
    # Index exceptions
    IndexError,
    IndexNotFound,
    IndexFoundError,
    # Query exceptions
    QueryError,
    QueryAbortedError,
    # Admin / UDF exceptions
    AdminError,
    UDFError,
)

__all__ = [
    "AerospikeError",
    "ClientError",
    "ServerError",
    "RecordError",
    "ClusterError",
    "TimeoutError",
    "InvalidArgError",
    "RecordNotFound",
    "RecordExistsError",
    "RecordGenerationError",
    "RecordTooBig",
    "BinNameError",
    "BinExistsError",
    "BinNotFound",
    "BinTypeError",
    "FilteredOut",
    "IndexError",
    "IndexNotFound",
    "IndexFoundError",
    "QueryError",
    "QueryAbortedError",
    "AdminError",
    "UDFError",
]
