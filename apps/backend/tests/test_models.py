import json
from datetime import datetime

from agent import (
    ContentCompleteMessage,
    ContentDeltaMessage,
    EndMessage,
    ErrorMessage,
    MessageType,
    StartMessage,
    ToolCallMessage,
    ToolResultMessage,
)


class TestMessageModels:
    """Test Pydantic model validation and serialization."""

    def test_message_type_enum(self):
        """Test MessageType enum values."""
        assert MessageType.START == "start"
        assert MessageType.TOOL_CALL == "tool_call"
        assert MessageType.TOOL_RESULT == "tool_result"
        assert MessageType.CONTENT_DELTA == "content_delta"
        assert MessageType.CONTENT_COMPLETE == "content_complete"
        assert MessageType.ERROR == "error"
        assert MessageType.END == "end"

    def test_start_message_serialization(self):
        """Test StartMessage model serialization."""
        msg = StartMessage()
        data = msg.model_dump()

        assert data["type"] == "start"
        assert "timestamp" in data
        # Verify timestamp is ISO format with Z suffix
        assert data["timestamp"].endswith("Z")
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

    def test_start_message_json_serialization(self):
        """Test StartMessage JSON serialization."""
        msg = StartMessage()
        json_str = json.dumps(msg.model_dump())
        assert isinstance(json_str, str)

        # Should be deserializable
        data = json.loads(json_str)
        assert data["type"] == "start"

    def test_tool_call_message_serialization(self):
        """Test ToolCallMessage model serialization."""
        msg = ToolCallMessage(
            tool_name="get_transactions",
            tool_args={"limit": 10},
            tool_call_id="call_123",
        )
        data = msg.model_dump()

        assert data["type"] == "tool_call"
        assert data["tool_name"] == "get_transactions"
        assert data["tool_args"] == {"limit": 10}
        assert data["tool_call_id"] == "call_123"

    def test_tool_result_message_serialization(self):
        """Test ToolResultMessage model serialization."""
        result_data = {"data": [{"id": "1", "amount": "10.00"}]}
        msg = ToolResultMessage(
            tool_call_id="call_123", tool_name="get_transactions", result=result_data
        )
        data = msg.model_dump()

        assert data["type"] == "tool_result"
        assert data["tool_call_id"] == "call_123"
        assert data["tool_name"] == "get_transactions"
        assert data["result"] == result_data

    def test_content_delta_message_serialization(self):
        """Test ContentDeltaMessage model serialization."""
        msg = ContentDeltaMessage(delta="Hello", accumulated="Hello")
        data = msg.model_dump()

        assert data["type"] == "content_delta"
        assert data["delta"] == "Hello"
        assert data["accumulated"] == "Hello"

    def test_content_complete_message_serialization(self):
        """Test ContentCompleteMessage model serialization."""
        msg = ContentCompleteMessage(content="Hello, world!")
        data = msg.model_dump()

        assert data["type"] == "content_complete"
        assert data["content"] == "Hello, world!"

    def test_error_message_serialization(self):
        """Test ErrorMessage model serialization."""
        msg = ErrorMessage(message="Something went wrong", code="TEST_ERROR")
        data = msg.model_dump()

        assert data["type"] == "error"
        assert data["message"] == "Something went wrong"
        assert data["code"] == "TEST_ERROR"

    def test_error_message_default_code(self):
        """Test ErrorMessage default error code."""
        msg = ErrorMessage(message="Something went wrong")
        data = msg.model_dump()

        assert data["code"] == "UNKNOWN_ERROR"

    def test_end_message_serialization(self):
        """Test EndMessage model serialization."""
        msg = EndMessage()
        data = msg.model_dump()

        assert data["type"] == "end"
        assert "timestamp" in data
        assert data["timestamp"].endswith("Z")
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
