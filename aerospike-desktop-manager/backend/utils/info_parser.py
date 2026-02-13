"""Aerospike info response parser utilities."""


def parse_info_pairs(response: str) -> dict[str, str]:
    """Parse 'key=value;key=value' into a dict."""
    result = {}
    if not response:
        return result
    for pair in response.split(";"):
        pair = pair.strip()
        if "=" in pair:
            k, v = pair.split("=", 1)
            result[k] = v
    return result


def parse_info_list(response: str) -> list[str]:
    """Parse 'item;item;item' into a list."""
    if not response:
        return []
    return [item.strip() for item in response.split(";") if item.strip()]


def parse_set_info(response: str) -> list[dict]:
    """Parse set info response into list of dicts.

    Format: 'ns=test:set=users:objects=100:...; ns=test:set=products:...'
    """
    result = []
    if not response:
        return result
    for entry in response.split(";"):
        entry = entry.strip()
        if not entry:
            continue
        record = {}
        for pair in entry.split(":"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                record[k] = v
        if record:
            result.append(record)
    return result


def parse_sindex_info(response: str) -> list[dict]:
    """Parse secondary index info response.

    Format: 'ns=test:indexname=idx1:set=users:bin=age:type=numeric:...; ...'
    """
    return parse_set_info(response)
