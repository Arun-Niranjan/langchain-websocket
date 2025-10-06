import logging

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute

from agent import AgentWebSocket, bootstrap_agent
from config import settings

logger = logging.getLogger("uvicorn")

agent = bootstrap_agent(settings)
aws = AgentWebSocket(
    agent,
    logger,
)


async def health_check(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


app = Starlette(
    routes=[
        Route("/health", health_check),
        WebSocketRoute("/ws/agent", aws.agent_websocket_endpoint),
    ],
)
