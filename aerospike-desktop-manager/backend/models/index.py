"""Secondary index models."""

from pydantic import BaseModel


class IndexInfo(BaseModel):
    name: str
    namespace: str
    set_name: str = ""
    bin_name: str = ""
    index_type: str = ""  # numeric, string, geo2dsphere
    state: str = ""
    raw: dict[str, str] = {}


class CreateIndexRequest(BaseModel):
    set_name: str
    bin_name: str
    index_name: str
    index_type: str = "numeric"  # numeric, string, geo2dsphere
