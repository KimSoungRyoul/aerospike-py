"""Admin (user/role management) router."""

import aerospike_py
from fastapi import APIRouter, Depends

from dependencies import get_client
from models.admin import (
    ChangePasswordRequest,
    CreateRoleRequest,
    CreateUserRequest,
    GrantRevokePrivilegesRequest,
    GrantRevokeRolesRequest,
    SetQuotasRequest,
    SetWhitelistRequest,
)

router = APIRouter()

# ── User management ───────────────────────────────────────────


@router.get("/users")
async def list_users(
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    return await client.admin_query_users_info()


@router.get("/users/{username}")
async def get_user(
    username: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    return await client.admin_query_user_info(username)


@router.post("/users")
async def create_user(
    req: CreateUserRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_create_user(req.username, req.password, req.roles)
    return {"ok": True}


@router.delete("/users/{username}")
async def drop_user(
    username: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_drop_user(username)
    return {"ok": True}


@router.put("/users/{username}/password")
async def change_password(
    username: str,
    req: ChangePasswordRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_change_password(username, req.password)
    return {"ok": True}


@router.post("/users/{username}/grant-roles")
async def grant_roles(
    username: str,
    req: GrantRevokeRolesRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_grant_roles(username, req.roles)
    return {"ok": True}


@router.post("/users/{username}/revoke-roles")
async def revoke_roles(
    username: str,
    req: GrantRevokeRolesRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_revoke_roles(username, req.roles)
    return {"ok": True}


# ── Role management ───────────────────────────────────────────


@router.get("/roles")
async def list_roles(
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    return await client.admin_query_roles()


@router.get("/roles/{role}")
async def get_role(
    role: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    return await client.admin_query_role(role)


@router.post("/roles")
async def create_role(
    req: CreateRoleRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_create_role(
        req.role,
        req.privileges,
        whitelist=req.whitelist,
        read_quota=req.read_quota,
        write_quota=req.write_quota,
    )
    return {"ok": True}


@router.delete("/roles/{role}")
async def drop_role(
    role: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_drop_role(role)
    return {"ok": True}


@router.post("/roles/{role}/grant-privileges")
async def grant_privileges(
    role: str,
    req: GrantRevokePrivilegesRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_grant_privileges(role, req.privileges)
    return {"ok": True}


@router.post("/roles/{role}/revoke-privileges")
async def revoke_privileges(
    role: str,
    req: GrantRevokePrivilegesRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_revoke_privileges(role, req.privileges)
    return {"ok": True}


@router.put("/roles/{role}/whitelist")
async def set_whitelist(
    role: str,
    req: SetWhitelistRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_set_whitelist(role, req.whitelist)
    return {"ok": True}


@router.put("/roles/{role}/quotas")
async def set_quotas(
    role: str,
    req: SetQuotasRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.admin_set_quotas(role, req.read_quota, req.write_quota)
    return {"ok": True}
