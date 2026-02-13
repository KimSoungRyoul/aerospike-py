"""Admin (user/role management) models."""

from typing import Any

from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    password: str
    roles: list[str]


class ChangePasswordRequest(BaseModel):
    password: str


class GrantRevokeRolesRequest(BaseModel):
    roles: list[str]


class CreateRoleRequest(BaseModel):
    role: str
    privileges: list[dict[str, Any]]
    whitelist: list[str] | None = None
    read_quota: int = 0
    write_quota: int = 0


class GrantRevokePrivilegesRequest(BaseModel):
    privileges: list[dict[str, Any]]


class SetWhitelistRequest(BaseModel):
    whitelist: list[str]


class SetQuotasRequest(BaseModel):
    read_quota: int = 0
    write_quota: int = 0
