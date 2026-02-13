"""Integration tests for info() / info_all() — requires Aerospike server."""

import pytest


class TestSyncInfo:
    """Tests for Client.info() and Client.info_all()."""

    def test_info_node(self, client):
        """info(['node']) should return the node name."""
        result = client.info(["node"])
        assert isinstance(result, dict)
        assert "node" in result
        assert len(result["node"]) > 0  # node name is non-empty

    def test_info_namespaces(self, client):
        """info(['namespaces']) should return semicolon-separated NS list."""
        result = client.info(["namespaces"])
        assert "namespaces" in result
        ns_list = result["namespaces"].split(";")
        assert "test" in ns_list

    def test_info_build(self, client):
        """info(['build']) returns the server build version."""
        result = client.info(["build"])
        assert "build" in result
        assert len(result["build"]) > 0

    def test_info_multiple_commands(self, client):
        """Multiple info commands in a single call."""
        result = client.info(["node", "build", "edition"])
        assert "node" in result
        assert "build" in result
        assert "edition" in result

    def test_info_statistics(self, client):
        """info(['statistics']) returns key=value pairs."""
        result = client.info(["statistics"])
        assert "statistics" in result
        # statistics response is key=value pairs separated by ;
        assert "=" in result["statistics"]

    def test_info_sets(self, client, cleanup):
        """info(['sets/test']) should list sets in the 'test' namespace."""
        # Ensure at least one record exists
        key = ("test", "info_test_set", "rec1")
        cleanup.append(key)
        client.put(key, {"a": 1})

        result = client.info(["sets/test"])
        assert "sets/test" in result

    def test_info_bins(self, client, cleanup):
        """info(['bins/test']) should list bin names."""
        key = ("test", "info_test_bins", "rec1")
        cleanup.append(key)
        client.put(key, {"mybin": "val"})

        result = client.info(["bins/test"])
        assert "bins/test" in result

    def test_info_with_specific_node(self, client):
        """info() with explicit node_name parameter."""
        node_names = client.get_node_names()
        assert len(node_names) > 0

        result = client.info(["node"], node_name=node_names[0])
        assert "node" in result
        assert result["node"] == node_names[0]

    def test_info_all_returns_all_nodes(self, client):
        """info_all() should return results for every cluster node."""
        result = client.info_all(["node"])
        assert isinstance(result, dict)

        node_names = client.get_node_names()
        assert len(result) == len(node_names)

        for node_name in node_names:
            assert node_name in result
            assert "node" in result[node_name]
            assert result[node_name]["node"] == node_name

    def test_info_all_namespaces(self, client):
        """info_all(['namespaces']) returns NS list from all nodes."""
        result = client.info_all(["namespaces"])
        for node_name, info_dict in result.items():
            assert "namespaces" in info_dict
            assert "test" in info_dict["namespaces"]


class TestAsyncInfo:
    """Tests for AsyncClient.info() and AsyncClient.info_all()."""

    @pytest.mark.asyncio
    async def test_info_node(self, async_client):
        result = await async_client.info(["node"])
        assert isinstance(result, dict)
        assert "node" in result
        assert len(result["node"]) > 0

    @pytest.mark.asyncio
    async def test_info_namespaces(self, async_client):
        result = await async_client.info(["namespaces"])
        assert "namespaces" in result
        assert "test" in result["namespaces"]

    @pytest.mark.asyncio
    async def test_info_multiple_commands(self, async_client):
        result = await async_client.info(["node", "build", "edition"])
        assert "node" in result
        assert "build" in result
        assert "edition" in result

    @pytest.mark.asyncio
    async def test_info_all_returns_all_nodes(self, async_client):
        result = await async_client.info_all(["node"])
        assert isinstance(result, dict)
        assert len(result) > 0

        for node_name, info_dict in result.items():
            assert "node" in info_dict

    @pytest.mark.asyncio
    async def test_info_with_specific_node(self, async_client):
        node_names = await async_client.get_node_names()
        assert len(node_names) > 0

        result = await async_client.info(["node"], node_name=node_names[0])
        assert result["node"] == node_names[0]
