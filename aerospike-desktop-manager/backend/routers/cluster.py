"""Cluster overview and node detail router."""

import aerospike_py
from fastapi import APIRouter, Depends

from dependencies import get_client
from models.cluster import ClusterOverview, NodeInfo
from utils.info_parser import parse_info_list, parse_info_pairs

router = APIRouter()


@router.get("", response_model=ClusterOverview)
async def get_cluster_overview(
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info_all(["node", "build", "edition", "namespaces"])
    nodes = []
    all_namespaces = set()
    edition = ""
    build = ""

    for node_name, info_dict in result.items():
        ns_str = info_dict.get("namespaces", "")
        ns_list = parse_info_list(ns_str)
        all_namespaces.update(ns_list)
        edition = info_dict.get("edition", edition)
        build = info_dict.get("build", build)
        nodes.append(
            NodeInfo(
                name=node_name,
                build=info_dict.get("build", ""),
                edition=info_dict.get("edition", ""),
                namespaces=ns_list,
            )
        )

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
    result = await client.info_all(["node", "build", "edition", "namespaces"])
    nodes = []
    for node_name, info_dict in result.items():
        ns_list = parse_info_list(info_dict.get("namespaces", ""))
        nodes.append(
            NodeInfo(
                name=node_name,
                build=info_dict.get("build", ""),
                edition=info_dict.get("edition", ""),
                namespaces=ns_list,
            )
        )
    return nodes


@router.get("/nodes/{node_name}")
async def get_node_statistics(
    node_name: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info(["statistics"], node_name=node_name)
    return parse_info_pairs(result.get("statistics", ""))
