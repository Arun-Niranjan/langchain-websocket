import json

from starlette.testclient import TestClient

from main import app


class TestToolCallTracking:
    """Test tool call tracking and result association."""

    def test_tool_call_has_required_fields(self):
        """Test that TOOL_CALL messages have all required fields."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.send_text("Show me my transactions")

            tool_call_msg = None
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "tool_call":
                    tool_call_msg = msg
                    break

                if msg["type"] == "end":
                    break

            # Should have found a tool call
            assert tool_call_msg is not None

            # Verify required fields
            assert "tool_name" in tool_call_msg
            assert "tool_args" in tool_call_msg
            assert "tool_call_id" in tool_call_msg

            # tool_name should be the function name
            assert tool_call_msg["tool_name"] == "get_transactions"

            # tool_call_id should be a non-empty string
            assert isinstance(tool_call_msg["tool_call_id"], str)
            assert len(tool_call_msg["tool_call_id"]) > 0

    def test_tool_result_matches_tool_call(self):
        """Test that TOOL_RESULT is associated with the correct TOOL_CALL."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.send_text("Get my transaction history")

            tool_call_id = None
            tool_result_msg = None

            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "tool_call":
                    tool_call_id = msg["tool_call_id"]

                if msg["type"] == "tool_result":
                    tool_result_msg = msg
                    break

                if msg["type"] == "end":
                    break

            # Should have both tool call and tool result
            assert tool_call_id is not None
            assert tool_result_msg is not None

            # Tool result should reference the same tool_call_id
            assert tool_result_msg["tool_call_id"] == tool_call_id

            # Tool result should have the correct tool name
            assert tool_result_msg["tool_name"] == "get_transactions"

    def test_tool_result_contains_data(self):
        """Test that TOOL_RESULT contains the expected data structure."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.send_text("What transactions do I have?")

            tool_result_msg = None

            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "tool_result":
                    tool_result_msg = msg
                    break

                if msg["type"] == "end":
                    break

            # Should have found a tool result
            assert tool_result_msg is not None

            # Result should contain data field with list
            assert "result" in tool_result_msg
            assert "data" in tool_result_msg["result"]
            assert isinstance(tool_result_msg["result"]["data"], list)

            # Should have transaction data
            data = tool_result_msg["result"]["data"]
            assert len(data) > 0

            # Each transaction should have expected fields
            for transaction in data:
                assert "id" in transaction
                assert "amount" in transaction
                assert "date_time" in transaction

    def test_multiple_tool_calls(self):
        """Test handling of multiple tool calls if they occur."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # This might trigger multiple tool calls depending on agent behavior
            websocket.send_text("Show me transactions twice")

            tool_calls = []
            tool_results = []

            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "tool_call":
                    tool_calls.append(msg)

                if msg["type"] == "tool_result":
                    tool_results.append(msg)

                if msg["type"] == "end":
                    break

            # Should have at least one tool call
            assert len(tool_calls) >= 1
            assert len(tool_results) >= 1

            # Each tool result should match a tool call ID
            tool_call_ids = {tc["tool_call_id"] for tc in tool_calls}
            for result in tool_results:
                assert result["tool_call_id"] in tool_call_ids
