"""Cluster overview and node detail router."""

import aerospike_py
from fastapi import APIRouter, Depends

from dependencies import get_client
from models.cluster import ClusterOverview, NodeInfo
from utils.info_parser import parse_info_list, parse_info_pairs

router = APIRouter()

_CLUSTER_INFO_COMMANDS = ["node", "build", "edition", "namespaces"]


def _build_node_list(result: dict) -> list[NodeInfo]:
    return [
        NodeInfo(
            name=node_name,
            build=info_dict.get("build", ""),
            edition=info_dict.get("edition", ""),
            namespaces=parse_info_list(info_dict.get("namespaces", "")),
        )
        for node_name, info_dict in result.items()
    ]


@router.get("", response_model=ClusterOverview)
async def get_cluster_overview(
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info_all(_CLUSTER_INFO_COMMANDS)
    nodes = _build_node_list(result)

    all_namespaces: set[str] = set()
    edition = ""
    build = ""
    for node in nodes:
        all_namespaces.update(node.namespaces)
        edition = node.edition or edition
        build = node.build or build

    return ClusterOverview(
        nodes=nodes,
        namespaces=sorted(all_namespaces),
        node_count=len(nodes),
        edition=edition,
        build=build,
    )


@router.get("/nodes", response_model=list[NodeInfo])
async def get_cluster_nodes(
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info_all(_CLUSTER_INFO_COMMANDS)
    return _build_node_list(result)


@router.get("/nodes/{node_name}")
async def get_node_statistics(
    node_name: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info(["statistics"], node_name=node_name)
    return parse_info_pairs(result.get("statistics", ""))
