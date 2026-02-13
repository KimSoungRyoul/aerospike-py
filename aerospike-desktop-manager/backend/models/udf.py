"""UDF models."""

from typing import Any

from pydantic import BaseModel


class UdfInfo(BaseModel):
    filename: str
    hash: str = ""
    type: str = "LUA"


class UdfUploadRequest(BaseModel):
    filename: str
    content: str  # Base64-encoded Lua source


class UdfExecuteRequest(BaseModel):
    namespace: str
    set_name: str
    key: str | int
    module: str
    function: str
    args: list[Any] = []
