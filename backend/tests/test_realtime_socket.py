"""
Integration test for the Socket.IO realtime layer.

Starts the real ASGI socket app on an HTTP server (lifespan disabled, so no
database is needed) and verifies authentication, room join and event delivery
end to end over the wire.
"""
import asyncio
import socket

import pytest
import pytest_asyncio
import socketio
import uvicorn

from app.core.security import create_access_token
from app.main import socket_app
from app.realtime.server import emit_notification


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest_asyncio.fixture
async def realtime_server():
    port = _free_port()
    config = uvicorn.Config(
        socket_app, host="127.0.0.1", port=port, log_level="warning", lifespan="off"
    )
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())

    for _ in range(200):
        if server.started:
            break
        await asyncio.sleep(0.05)
    assert server.started, "uvicorn did not start"

    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        try:
            await asyncio.wait_for(task, timeout=10)
        except asyncio.TimeoutError:  # pragma: no cover
            task.cancel()


async def test_socket_receives_notification(realtime_server: str) -> None:
    user_id = "11111111-1111-1111-1111-111111111111"
    token = create_access_token(subject=user_id)

    client = socketio.AsyncClient()
    received: asyncio.Future = asyncio.get_running_loop().create_future()

    @client.on("notification")
    async def _on_notification(data):  # noqa: ANN001
        if not received.done():
            received.set_result(data)

    await client.connect(realtime_server, auth={"token": token})
    # give the connect handler a moment to join the room
    await asyncio.sleep(0.2)

    try:
        await emit_notification(
            user_id,
            {
                "id": "n1",
                "type": "favorite",
                "recipe_slug": "tarta-de-manzana",
                "recipe_title": "Tarta de manzana",
                "in_app": True,
            },
        )
        result = await asyncio.wait_for(received, timeout=5)
        assert result["recipe_title"] == "Tarta de manzana"
    finally:
        await client.disconnect()


async def test_socket_rejects_missing_token(realtime_server: str) -> None:
    client = socketio.AsyncClient()
    try:
        with pytest.raises(socketio.exceptions.ConnectionError):
            await client.connect(realtime_server)
    finally:
        await client.disconnect()
