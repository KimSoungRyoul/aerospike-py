"""Record value serialization utilities."""

from typing import Any


def detect_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        if value.startswith('{"type"') and "coordinates" in value:
            return "geojson"
        return "string"
    if isinstance(value, bytes):
        return "bytes"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "map"
    return "unknown"


def serialize_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, dict):
        return {str(k): serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize_value(v) for v in value]
    return value


def serialize_key(key: Any) -> Any:
    """Convert bytes fields (e.g. digest) in an Aerospike key tuple to hex strings."""
    if key is None:
        return None
    if isinstance(key, (list, tuple)):
        return tuple(v.hex() if isinstance(v, bytes) else v for v in key)
    return key


def format_bins(bins: dict[str, Any] | None) -> dict[str, Any]:
    if not bins:
        return {}
    result = {}
    for name, value in bins.items():
        result[name] = {
            "value": serialize_value(value),
            "type": detect_type(value),
        }
    return result


def format_record(rec: tuple) -> dict:
    """Format a raw (key, meta, bins) record tuple into a response dict."""
    key, meta, bins = rec
    return {
        "key": serialize_key(key),
        "meta": meta,
        "bins": format_bins(bins),
    }
