"""Unit tests for get_server_version() (no server required)."""

from unittest.mock import AsyncMock, patch

import pytest

import aerospike_py
from aerospike_py._async_client import AsyncClient
from tests import DUMMY_CONFIG


class TestClientGetServerVersion:
    """Sync Client.get_server_version() tests."""

    def test_parses_standard_response(self):
        """Extracts version from standard 'build\\t8.1.0.3\\n' format."""
        with patch.object(aerospike_py.Client, "info_random_node", return_value="build\t8.1.0.3\n"):
            c = aerospike_py.client(DUMMY_CONFIG)
            assert c.get_server_version() == "8.1.0.3"

    def test_strips_whitespace(self):
        """Strips trailing whitespace/newlines from parsed version."""
        with patch.object(aerospike_py.Client, "info_random_node", return_value="build\t7.0.0.0  \n"):
            c = aerospike_py.client(DUMMY_CONFIG)
            assert c.get_server_version() == "7.0.0.0"

    def test_fallback_on_unexpected_format(self):
        """Falls back to stripped response when no tab separator found."""
        with patch.object(aerospike_py.Client, "info_random_node", return_value="8.1.0.3\n"):
            c = aerospike_py.client(DUMMY_CONFIG)
            assert c.get_server_version() == "8.1.0.3"

    def test_empty_response(self):
        """Handles empty response gracefully."""
        with patch.object(aerospike_py.Client, "info_random_node", return_value=""):
            c = aerospike_py.client(DUMMY_CONFIG)
            assert c.get_server_version() == ""


class TestAsyncClientGetServerVersion:
    """Async AsyncClient.get_server_version() tests."""

    @pytest.mark.asyncio
    async def test_parses_standard_response(self):
        """Extracts version from standard 'build\\t8.1.0.3\\n' format."""
        with patch.object(AsyncClient, "info_random_node", new_callable=AsyncMock, return_value="build\t8.1.0.3\n"):
            c = AsyncClient(DUMMY_CONFIG)
            assert await c.get_server_version() == "8.1.0.3"

    @pytest.mark.asyncio
    async def test_fallback_on_unexpected_format(self):
        """Falls back to stripped response when no tab separator found."""
        with patch.object(AsyncClient, "info_random_node", new_callable=AsyncMock, return_value="8.1.0.3\n"):
            c = AsyncClient(DUMMY_CONFIG)
            assert await c.get_server_version() == "8.1.0.3"

    @pytest.mark.asyncio
    async def test_empty_response(self):
        """Handles empty response gracefully."""
        with patch.object(AsyncClient, "info_random_node", new_callable=AsyncMock, return_value=""):
            c = AsyncClient(DUMMY_CONFIG)
            assert await c.get_server_version() == ""
