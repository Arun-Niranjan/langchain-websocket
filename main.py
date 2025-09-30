import asyncio
import logging
from dataclasses import asdict

from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.schema import StreamEvent
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from models import ChatResponse, Message, MessageType

logger = logging.getLogger("uvicorn")


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
                type=MessageType.STREAM,
            )
        case "on_parser_end":
            return ChatResponse(
                source="bot",
                message=event.get("data", {}).get("output", ""),
                type=MessageType.END,
            )
        case _:
            return None


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                user_msg = await asyncio.wait_for(websocket.receive_text(), timeout=15.0)
            except TimeoutError:
                await websocket.send_json(
                    asdict(
                        ChatResponse(
                            source="bot",
                            message=Message(content="Connection timed out due to user inactivity."),
                            type=MessageType.ERROR,
                        )
                    )
                )
                logger.info("Closing connection due to user inactivity")
                await websocket.close(code=1000)
                break

            start_resp = ChatResponse(source="bot", message=Message(), type=MessageType.START)
            await websocket.send_json(asdict(start_resp))
            try:
                async for event in chain.astream_events({"input": user_msg}):
                    resp = get_response_from_event(event)
                    if resp:
                        await websocket.send_json(asdict(resp))
            except Exception as e:
                logger.error(f"Error processing chain events: {e}")
                err_resp = ChatResponse(
                    source="bot",
                    message=Message(content="error processing message, please try again later."),
                    type=MessageType.ERROR,
                )
                await websocket.send_json(asdict(err_resp))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Chatbot encountered error: {e}")


app = Starlette(routes=[WebSocketRoute("/ws/chat", websocket_endpoint)])
