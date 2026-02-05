"""Unit tests for import and basic module structure (no server required)."""

import aerospike
from aerospike import exception


def test_import():
    """Test that aerospike module can be imported."""
    assert hasattr(aerospike, "__version__")
    assert aerospike.__version__ == "0.1.0"


def test_client_factory():
    """Test that aerospike.client() creates a Client."""
    c = aerospike.client({"hosts": [("127.0.0.1", 3000)]})
    assert isinstance(c, aerospike.Client)
    assert not c.is_connected()


def test_client_not_connected_raises():
    """Test that calling methods on unconnected client raises ClientError."""
    c = aerospike.client({"hosts": [("127.0.0.1", 3000)]})
    try:
        c.get(("test", "demo", "key1"))
        assert False, "Should have raised ClientError"
    except aerospike.ClientError:
        pass


def test_constants():
    """Test that all key constants are defined."""
    # Policy Key
    assert aerospike.POLICY_KEY_DIGEST == 0
    assert aerospike.POLICY_KEY_SEND == 1

    # Policy Exists
    assert aerospike.POLICY_EXISTS_IGNORE == 0
    assert aerospike.POLICY_EXISTS_UPDATE == 1
    assert aerospike.POLICY_EXISTS_UPDATE_ONLY == 1
    assert aerospike.POLICY_EXISTS_REPLACE == 2
    assert aerospike.POLICY_EXISTS_REPLACE_ONLY == 3
    assert aerospike.POLICY_EXISTS_CREATE_ONLY == 4

    # Policy Gen
    assert aerospike.POLICY_GEN_IGNORE == 0
    assert aerospike.POLICY_GEN_EQ == 1
    assert aerospike.POLICY_GEN_GT == 2

    # TTL
    assert aerospike.TTL_NAMESPACE_DEFAULT == 0
    assert aerospike.TTL_NEVER_EXPIRE == -1
    assert aerospike.TTL_DONT_UPDATE == -2

    # Operators
    assert aerospike.OPERATOR_READ == 1
    assert aerospike.OPERATOR_WRITE == 2
    assert aerospike.OPERATOR_INCR == 5
    assert aerospike.OPERATOR_APPEND == 9
    assert aerospike.OPERATOR_PREPEND == 10
    assert aerospike.OPERATOR_TOUCH == 11
    assert aerospike.OPERATOR_DELETE == 12

    # Status codes
    assert aerospike.AEROSPIKE_OK == 0
    assert aerospike.AEROSPIKE_ERR_RECORD_NOT_FOUND == 2
    assert aerospike.AEROSPIKE_ERR_RECORD_EXISTS == 5
    assert aerospike.AEROSPIKE_ERR_TIMEOUT == 9


def test_exception_hierarchy():
    """Test that exception classes follow proper hierarchy."""
    assert issubclass(aerospike.ClientError, aerospike.AerospikeError)
    assert issubclass(aerospike.ServerError, aerospike.AerospikeError)
    assert issubclass(aerospike.RecordError, aerospike.AerospikeError)
    assert issubclass(aerospike.ClusterError, aerospike.AerospikeError)
    assert issubclass(aerospike.TimeoutError, aerospike.AerospikeError)
    assert issubclass(aerospike.InvalidArgError, aerospike.AerospikeError)

    # Record-level subclasses
    assert issubclass(aerospike.RecordNotFound, aerospike.RecordError)
    assert issubclass(aerospike.RecordExistsError, aerospike.RecordError)
    assert issubclass(aerospike.RecordGenerationError, aerospike.RecordError)
    assert issubclass(aerospike.RecordTooBig, aerospike.RecordError)
    assert issubclass(aerospike.BinNameError, aerospike.RecordError)
    assert issubclass(aerospike.BinExistsError, aerospike.RecordError)
    assert issubclass(aerospike.BinNotFound, aerospike.RecordError)
    assert issubclass(aerospike.BinTypeError, aerospike.RecordError)
    assert issubclass(aerospike.FilteredOut, aerospike.RecordError)

    # Same classes accessible from exception module
    assert issubclass(exception.RecordNotFound, aerospike.RecordError)
    assert issubclass(exception.RecordExistsError, aerospike.RecordError)
    assert issubclass(exception.BinNameError, aerospike.RecordError)
    assert issubclass(exception.IndexNotFound, exception.IndexError)
    assert issubclass(exception.QueryAbortedError, exception.QueryError)
    assert issubclass(exception.AdminError, aerospike.ServerError)
    assert issubclass(exception.UDFError, aerospike.ServerError)

    # Verify exception module classes are the same objects as aerospike module classes
    assert exception.RecordNotFound is aerospike.RecordNotFound
    assert exception.IndexNotFound is aerospike.IndexNotFound


def test_client_not_connected_operations():
    """Test that various methods on unconnected client raise ClientError."""
    c = aerospike.client({"hosts": [("127.0.0.1", 3000)]})
    key = ("test", "demo", "key1")

    for method, args in [
        ("put", (key, {"a": 1})),
        ("exists", (key,)),
        ("remove", (key,)),
        ("select", (key, ["a"])),
        ("touch", (key,)),
        ("append", (key, "a", "val")),
        ("prepend", (key, "a", "val")),
        ("increment", (key, "a", 1)),
    ]:
        try:
            getattr(c, method)(*args)
            assert False, f"{method}() should have raised ClientError"
        except aerospike.ClientError:
            pass


def test_connect_username_without_password():
    """Test that connect() with username but no password raises ClientError."""
    c = aerospike.client({"hosts": [("127.0.0.1", 3000)]})
    try:
        c.connect(username="admin")
        assert False, "Should have raised ClientError"
    except aerospike.ClientError:
        pass
