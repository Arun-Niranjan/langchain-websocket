import asyncio
from datetime import UTC, datetime
from enum import StrEnum
from logging import Logger
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessageChunk, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from starlette.websockets import WebSocket, WebSocketDisconnect
import uuid
import json


# WebSocket Message Types
class MessageType(StrEnum):
    START = "start"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    CONTENT_DELTA = "content_delta"
    CONTENT_COMPLETE = "content_complete"
    ERROR = "error"
    END = "end"


# WebSocket API Models
class StartMessage(BaseModel):
    type: MessageType = MessageType.START
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat().replace("+00:00", "Z")
    )


class ToolCallMessage(BaseModel):
    type: MessageType = MessageType.TOOL_CALL
    tool_name: str
    tool_args: dict[str, Any]
    tool_call_id: str


class ToolResultMessage(BaseModel):
    type: MessageType = MessageType.TOOL_RESULT
    tool_call_id: str
    tool_name: str
    result: Any


class ContentDeltaMessage(BaseModel):
    type: MessageType = MessageType.CONTENT_DELTA
    delta: str
    accumulated: str


class ContentCompleteMessage(BaseModel):
    type: MessageType = MessageType.CONTENT_COMPLETE
    content: str


class ErrorMessage(BaseModel):
    type: MessageType = MessageType.ERROR
    message: str
    code: str = "UNKNOWN_ERROR"


class EndMessage(BaseModel):
    type: MessageType = MessageType.END
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat().replace("+00:00", "Z")
    )


def get_transactions() -> dict[str, Any]:
    """Get financial transactions."""
    return {
        "data": [
            {
                "id": "1",
                "amount": "-10.99",
                "date_time": "2025-10-05T00:00:00Z",
            },
            {
                "id": "2",
                "amount": "100.45",
                "date_time": "2025-10-04T00:00:00Z",
            },
        ]
    }


model = init_chat_model("gpt-4o-mini", model_provider="openai")
memory = MemorySaver()

agent = create_react_agent(
    model=model,
    tools=[get_transactions],
    prompt="You are a helpful financial assistant.",
    checkpointer=memory,
)


def get_agent_websocket_endpoint(logger: Logger):
    async def agent_websocket_endpoint(websocket: WebSocket):
        await websocket.accept()

        session_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": session_id}}

        try:
            while True:
                try:
                    user_msg = await asyncio.wait_for(websocket.receive_text(), timeout=15.0)
                except TimeoutError:
                    await websocket.send_json(
                        ErrorMessage(
                            message="Connection timed out due to user inactivity.",
                            code="TIMEOUT",
                        ).model_dump()
                    )
                    logger.info("Closing connection due to user inactivity")
                    await websocket.close(code=1000)
                    break

                # Send START message
                await websocket.send_json(StartMessage().model_dump())

                try:
                    accumulated_content = ""
                    tool_call_map = {}  # Map tool_call_id to tool name

                    async for message_chunk, metadata in agent.astream(
                        {"messages": [{"role": "user", "content": user_msg}]},
                        stream_mode="messages",
                        config=config,
                    ):
                        # Handle tool calls
                        if isinstance(message_chunk, AIMessageChunk):
                            if hasattr(message_chunk, "tool_calls") and message_chunk.tool_calls:
                                for tool_call in message_chunk.tool_calls:
                                    tool_call_id = tool_call.get("id")
                                    tool_name = tool_call.get("name")
                                    tool_args = tool_call.get("args", {})

                                    if tool_call_id and tool_name:
                                        # Store tool call mapping
                                        tool_call_map[tool_call_id] = tool_name

                                        # Send TOOL_CALL message
                                        await websocket.send_json(
                                            ToolCallMessage(
                                                tool_name=tool_name,
                                                tool_args=tool_args,
                                                tool_call_id=tool_call_id,
                                            ).model_dump()
                                        )

                            # Handle content streaming
                            if message_chunk.content:
                                accumulated_content += message_chunk.content
                                await websocket.send_json(
                                    ContentDeltaMessage(
                                        delta=message_chunk.content,
                                        accumulated=accumulated_content,
                                    ).model_dump()
                                )

                        # Handle tool results
                        elif isinstance(message_chunk, ToolMessage):
                            tool_call_id = message_chunk.tool_call_id
                            tool_name = tool_call_map.get(tool_call_id, message_chunk.name)

                            try:
                                result = json.loads(message_chunk.content)
                            except json.JSONDecodeError:
                                result = message_chunk.content

                            await websocket.send_json(
                                ToolResultMessage(
                                    tool_call_id=tool_call_id,
                                    tool_name=tool_name,
                                    result=result,
                                ).model_dump()
                            )

                    # Send CONTENT_COMPLETE message
                    if accumulated_content:
                        await websocket.send_json(
                            ContentCompleteMessage(content=accumulated_content).model_dump()
                        )

                    # Send END message
                    await websocket.send_json(EndMessage().model_dump())

                except Exception as e:
                    logger.error(f"Error processing agent events: {e}")
                    await websocket.send_json(
                        ErrorMessage(
                            message="Error processing message, please try again later.",
                            code="PROCESSING_ERROR",
                        ).model_dump()
                    )

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"Agent encountered error: {e}")

    return agent_websocket_endpoint
