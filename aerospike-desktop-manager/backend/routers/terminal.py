"""Info command terminal router."""

import aerospike_py
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dependencies import get_client
from utils.info_parser import parse_info_pairs

router = APIRouter()


class TerminalCommand(BaseModel):
    command: str
    node_name: str | None = None


@router.post("")
async def execute_info_command(
    req: TerminalCommand,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    commands = [cmd.strip() for cmd in req.command.split("\n") if cmd.strip()]
    if not commands:
        return {"raw": {}, "parsed": {}}

    result = await client.info(commands, node_name=req.node_name)

    parsed = {}
    for cmd, response in result.items():
        if "=" in response and ";" in response:
            parsed[cmd] = parse_info_pairs(response)
        else:
            parsed[cmd] = response

    return {"raw": result, "parsed": parsed}


@router.post("/info-all")
async def execute_info_all_command(
    req: TerminalCommand,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    commands = [cmd.strip() for cmd in req.command.split("\n") if cmd.strip()]
    if not commands:
        return {}

    result = await client.info_all(commands)
    return result
