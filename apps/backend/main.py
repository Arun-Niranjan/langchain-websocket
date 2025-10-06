import logging

from starlette.applications import Starlette
from starlette.routing import WebSocketRoute

from agent import agent, AgentWebSocket

logger = logging.getLogger("uvicorn")

aws = AgentWebSocket(
    agent,
    logger,
)

app = Starlette(
    routes=[
        WebSocketRoute("/ws/agent", aws.agent_websocket_endpoint),
    ],
)
