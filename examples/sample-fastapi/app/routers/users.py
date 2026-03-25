from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Request

from aerospike_py import AsyncClient
from app.config import settings
from app.models import MessageResponse, UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

NS = settings.aerospike_namespace
SET = settings.aerospike_set


def _get_client(request: Request) -> AsyncClient:
    return request.app.state.aerospike


def _key(user_id: str) -> tuple[str, str, str]:
    return (NS, SET, user_id)


def _to_response(user_id: str, meta: dict, bins: dict) -> UserResponse:
    return UserResponse(
        user_id=user_id,
        name=bins["name"],
        email=bins["email"],
        age=bins["age"],
        generation=meta.gen,
    )


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(body: UserCreate, request: Request):
    """Create a new user."""
    client = _get_client(request)
    user_id = uuid.uuid4().hex
    key = _key(user_id)

    bins = {"user_id": user_id, **body.model_dump()}
    await client.put(key, bins)

    _, meta, bins = await client.get(key)
    return _to_response(user_id, meta, bins)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, request: Request):
    """Get a user by ID.

    RecordNotFound is handled by the global exception handler (→ 404).
    """
    client = _get_client(request)
    _, meta, bins = await client.get(_key(user_id))
    return _to_response(user_id, meta, bins)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, body: UserUpdate, request: Request):
    """Update an existing user (partial update).

    RecordNotFound from the initial get is handled by the global handler (→ 404).
    """
    client = _get_client(request)
    key = _key(user_id)

    # Verify the record exists first (RecordNotFound → 404 via global handler)
    await client.get(key)

    update_bins = body.model_dump(exclude_none=True)
    if not update_bins:
        raise HTTPException(status_code=422, detail="No fields to update")

    await client.put(key, update_bins)

    _, meta, bins = await client.get(key)
    return _to_response(user_id, meta, bins)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: str, request: Request):
    """Delete a user by ID.

    RecordNotFound is handled by the global exception handler (→ 404).
    """
    client = _get_client(request)
    await client.remove(_key(user_id))
    return MessageResponse(message=f"User {user_id} deleted")


@router.get("", response_model=list[UserResponse])
async def list_users(request: Request):
    """List all users by scanning the set via query().results()."""
    client = _get_client(request)
    records = await client.query(NS, SET).results()
    result = []
    for key, meta, bins in records:
        if bins is None:
            continue
        # query()는 aerospike-core 알파 제한으로 user_key=None을 반환하므로
        # 생성 시 bins에 저장한 user_id를 우선 사용한다.
        user_id = bins.get("user_id") or (key[2] if key else None)
        if user_id is None or not isinstance(bins.get("name"), str):
            continue
        result.append(_to_response(str(user_id), meta, bins))
    return result
