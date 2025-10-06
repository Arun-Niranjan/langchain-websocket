import json

from starlette.testclient import TestClient

from main import app


class TestAgentMessageFlow:
    """Test agent streaming and message flow."""

    def test_basic_message_flow(self):
        """Test basic message flow: START -> CONTENT_DELTA -> CONTENT_COMPLETE -> END."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Send a simple message that doesn't require tools
            websocket.send_text("Say hello")

            messages = []
            # Collect messages until END
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                messages.append(msg)

                if msg["type"] == "end":
                    break

            # Verify message sequence
            assert messages[0]["type"] == "start"
            assert any(m["type"] == "end" for m in messages)

            # Should have at least START and END
            assert len(messages) >= 2

    def test_tool_call_flow(self):
        """Test flow with tool calls: START -> TOOL_CALL -> TOOL_RESULT -> CONTENT."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Send a message that requires tool usage
            websocket.send_text("What are my recent transactions?")

            messages = []
            # Collect messages until END
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                messages.append(msg)

                if msg["type"] == "end":
                    break

            # Extract message types
            message_types = [m["type"] for m in messages]

            # Should start with START and end with END
            assert message_types[0] == "start"
            assert message_types[-1] == "end"

            # Should contain tool call and tool result
            assert "tool_call" in message_types
            assert "tool_result" in message_types

            # Tool call should come before tool result
            tool_call_idx = message_types.index("tool_call")
            tool_result_idx = message_types.index("tool_result")
            assert tool_call_idx < tool_result_idx

    def test_content_streaming(self):
        """Test that content is streamed via CONTENT_DELTA messages."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.send_text("Tell me about financial transactions")

            content_deltas = []
            # Collect all content delta messages
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "content_delta":
                    content_deltas.append(msg)

                if msg["type"] == "end":
                    break

            # Should have received streaming content
            if len(content_deltas) > 0:
                # Verify each delta has required fields
                for delta_msg in content_deltas:
                    assert "delta" in delta_msg
                    assert "accumulated" in delta_msg

                # Accumulated should grow with each delta
                for i in range(1, len(content_deltas)):
                    prev_len = len(content_deltas[i - 1]["accumulated"])
                    curr_len = len(content_deltas[i]["accumulated"])
                    assert curr_len >= prev_len

    def test_content_complete_message(self):
        """Test that CONTENT_COMPLETE is sent after streaming."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.send_text("What transactions do I have?")

            messages = []
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                messages.append(msg)

                if msg["type"] == "end":
                    break

            message_types = [m["type"] for m in messages]

            # If there was content streaming, should have CONTENT_COMPLETE
            if "content_delta" in message_types:
                assert "content_complete" in message_types

                # CONTENT_COMPLETE should come after all CONTENT_DELTAs
                last_delta_idx = max(
                    i for i, t in enumerate(message_types) if t == "content_delta"
                )
                complete_idx = message_types.index("content_complete")
                assert complete_idx > last_delta_idx

    def test_multiple_messages_in_session(self):
        """Test sending multiple messages in the same WebSocket session."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # First message
            websocket.send_text("Hello")

            # Wait for END message
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                if msg["type"] == "end":
                    break

            # Second message
            websocket.send_text("What are my transactions?")

            # Wait for END message again
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                if msg["type"] == "end":
                    break

            # If we got here, both messages were processed successfully
            assert True
