"""Key parsing and building utilities."""


def parse_pk(pk: str) -> str | int:
    """Try to interpret PK as integer, fall back to string."""
    try:
        return int(pk)
    except ValueError:
        return pk


def build_key(ns: str, set_name: str, pk: str | int) -> tuple[str, str, str | int]:
    """Build an Aerospike key tuple."""
    return (ns, set_name, pk)
