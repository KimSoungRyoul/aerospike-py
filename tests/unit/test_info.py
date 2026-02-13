"""Unit tests for info() / info_all() method signatures (no server required)."""

import pytest

import aerospike_py


class TestInfoMethodSignatures:
    """Verify that info/info_all are accessible and have correct signatures."""

    def test_client_has_info_method(self):
        assert hasattr(aerospike_py.Client, "info")

    def test_client_has_info_all_method(self):
        assert hasattr(aerospike_py.Client, "info_all")

    def test_async_client_has_info_method(self):
        assert hasattr(aerospike_py.AsyncClient, "info")

    def test_async_client_has_info_all_method(self):
        assert hasattr(aerospike_py.AsyncClient, "info_all")

    def test_client_info_accepts_commands_list(self):
        """Client.info() should accept commands as first arg."""
        client = aerospike_py.Client({"hosts": [("127.0.0.1", 3000)]})
        # Should not raise TypeError for argument signature
        with pytest.raises(aerospike_py.ClientError, match="not connected"):
            client.info(["node"])

    def test_client_info_all_accepts_commands_list(self):
        """Client.info_all() should accept commands as first arg."""
        client = aerospike_py.Client({"hosts": [("127.0.0.1", 3000)]})
        with pytest.raises(aerospike_py.ClientError, match="not connected"):
            client.info_all(["node"])

    @pytest.mark.asyncio
    async def test_async_client_info_accepts_commands_list(self):
        """AsyncClient.info() should accept commands as first arg."""
        client = aerospike_py.AsyncClient({"hosts": [("127.0.0.1", 3000)]})
        with pytest.raises(aerospike_py.ClientError, match="not connected"):
            await client.info(["node"])

    @pytest.mark.asyncio
    async def test_async_client_info_all_accepts_commands_list(self):
        """AsyncClient.info_all() should accept commands as first arg."""
        client = aerospike_py.AsyncClient({"hosts": [("127.0.0.1", 3000)]})
        with pytest.raises(aerospike_py.ClientError, match="not connected"):
            await client.info_all(["node"])
