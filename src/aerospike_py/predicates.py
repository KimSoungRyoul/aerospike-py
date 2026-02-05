"""Predicate helpers for secondary index queries.

Usage:
    import aerospike_py
    from aerospike_py import predicates as p

    query = client.query("test", "demo")
    query.where(p.equals("age", 30))
    query.where(p.between("age", 18, 65))
"""


def equals(bin_name, val):
    """Create an equality predicate for a secondary index query."""
    return ("equals", bin_name, val)


def between(bin_name, min_val, max_val):
    """Create a range predicate for a secondary index query."""
    return ("between", bin_name, min_val, max_val)


def contains(bin_name, index_type, val):
    """Create a contains predicate for collection index queries.

    Args:
        bin_name: Name of the bin.
        index_type: Collection index type (INDEX_TYPE_LIST, INDEX_TYPE_MAPKEYS, INDEX_TYPE_MAPVALUES).
        val: The value to search for.
    """
    return ("contains", bin_name, index_type, val)


def geo_within_geojson_region(bin_name, geojson):
    """Create a geospatial 'within region' predicate."""
    return ("geo_within_geojson_region", bin_name, geojson)


def geo_within_radius(bin_name, lat, lng, radius):
    """Create a geospatial 'within radius' predicate."""
    return ("geo_within_radius", bin_name, lat, lng, radius)


def geo_contains_geojson_point(bin_name, geojson):
    """Create a geospatial 'contains point' predicate."""
    return ("geo_contains_point", bin_name, geojson)
