import logging

from starlette.applications import Starlette
from starlette.routing import WebSocketRoute

from agent import get_agent_websocket_endpoint

logger = logging.getLogger("uvicorn")

app = Starlette(
    routes=[
        WebSocketRoute("/ws/agent", get_agent_websocket_endpoint(logger)),
    ],
)
