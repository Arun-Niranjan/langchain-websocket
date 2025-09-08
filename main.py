import logging
from dataclasses import asdict, dataclass
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.schema import StreamEvent
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

logger = logging.getLogger("uvicorn")

@dataclass
class ChatResponse:
    source: str
    message: dict[str, Any]
    type: str


prompt_str = """
write a haiku about {input}.
Give your output in JSON format:
{{
    "title": "<title>",
    "haiku": "<haiku>"
}}
"""

model = init_chat_model("gpt-4o-mini", model_provider="openai")
prompt = ChatPromptTemplate.from_template(prompt_str)
json_parser = JsonOutputParser()
chain = prompt | model | json_parser


def get_response_from_event(event: StreamEvent) -> ChatResponse | None:
    kind = event["event"]
    match kind:
        case "on_parser_stream":
            return ChatResponse(
                source="bot",
                message=event.get("data", {}).get("chunk", ""),
                type="stream",
            )
        case "on_parser_end":
            return ChatResponse(
                source="bot",
                message=event.get("data", {}).get("output", ""),
                type="end",
            )
        case _:
            return None


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            user_msg = await websocket.receive_text()
            start_resp = ChatResponse(source="bot", message={}, type="start")
            await websocket.send_json(asdict(start_resp))
            async for event in chain.astream_events({"input": user_msg}):
                resp = get_response_from_event(event)
                if resp:
                    await websocket.send_json(asdict(resp))

        except WebSocketDisconnect:
            break
        except Exception as e:
            logger.error(f"Chatbot encountered error: {e}")
            err_resp = ChatResponse(
                source="bot",
                message={
                    "content": "error connecting to chat-bot, please try again later."
                },
                type="error",
            )
            await websocket.send_json(asdict(err_resp))
            break


app = Starlette(routes=[WebSocketRoute("/ws/chat", websocket_endpoint)])
