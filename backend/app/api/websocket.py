from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
import json

router = APIRouter()
connected_clients: Set[WebSocket] = set()


@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        connected_clients.discard(websocket)


async def broadcast(message: dict):
    stale = set()
    for client in connected_clients:
        try:
            await client.send_text(json.dumps(message))
        except Exception:
            stale.add(client)
    connected_clients.difference_update(stale)
