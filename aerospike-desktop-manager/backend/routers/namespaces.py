"""Namespace and set browsing router."""

import aerospike_py
from fastapi import APIRouter, Depends

from dependencies import get_client
from models.cluster import BinInfo, NamespaceStats, SetInfo
from utils.info_parser import parse_info_list, parse_info_pairs, parse_set_info

router = APIRouter()


@router.get("", response_model=list[str])
async def list_namespaces(
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info(["namespaces"])
    return parse_info_list(result.get("namespaces", ""))


@router.get("/{ns}", response_model=NamespaceStats)
async def get_namespace_detail(
    ns: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info([f"namespace/{ns}"])
    raw = parse_info_pairs(result.get(f"namespace/{ns}", ""))

    return NamespaceStats(
        name=ns,
        objects=int(raw.get("objects", 0)),
        memory_used_bytes=int(raw.get("memory_used_bytes", 0)),
        memory_total_bytes=int(raw.get("memory-size", 0)),
        memory_free_pct=float(raw.get("memory_free_pct", 0)),
        device_used_bytes=int(raw.get("device_used_bytes", 0)),
        device_total_bytes=int(raw.get("device_total_bytes", 0)),
        device_free_pct=float(raw.get("device_free_pct", 0)),
        replication_factor=int(raw.get("replication-factor", raw.get("repl-factor", 1))),
        stop_writes=raw.get("stop_writes", "false") == "true",
        high_water_disk_pct=float(raw.get("high-water-disk-pct", 0)),
        high_water_memory_pct=float(raw.get("high-water-memory-pct", 0)),
        raw=raw,
    )


@router.get("/{ns}/sets", response_model=list[SetInfo])
async def list_sets(
    ns: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info([f"sets/{ns}"])
    raw_sets = parse_set_info(result.get(f"sets/{ns}", ""))
    sets = []
    for s in raw_sets:
        sets.append(
            SetInfo(
                name=s.get("set", ""),
                objects=int(s.get("objects", 0)),
                memory_data_bytes=int(s.get("memory_data_bytes", 0)),
                stop_writes_count=int(s.get("stop-writes-count", 0)),
                truncate_lut=int(s.get("truncate_lut", 0)),
                raw=s,
            )
        )
    return sets


@router.get("/{ns}/bins", response_model=list[BinInfo])
async def list_bins(
    ns: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info([f"bins/{ns}"])
    raw = result.get(f"bins/{ns}", "")
    bins = []
    if "bin_names=" in raw:
        parts = parse_info_pairs(raw)
        bin_names_str = parts.get("bin_names", "")
        if bin_names_str:
            for name in bin_names_str.split(","):
                name = name.strip()
                if name:
                    bins.append(BinInfo(name=name))
    else:
        for line in raw.split(","):
            name = line.strip()
            if name:
                bins.append(BinInfo(name=name))
    return bins
