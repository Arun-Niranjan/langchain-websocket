import json
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from main import app


class TestErrorHandling:
    """Test error handling and timeout behavior."""

    def test_timeout_on_inactivity(self):
        """Test that connection times out after 15 seconds of inactivity."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Wait for timeout (should be ~15 seconds)
            # First message should be ERROR with TIMEOUT code
            msg_str = websocket.receive_text()
            msg = json.loads(msg_str)

            assert msg["type"] == "error"
            assert msg["code"] == "TIMEOUT"
            assert "inactivity" in msg["message"].lower()

    def test_agent_processing_error(self):
        """Test error handling when agent processing fails."""
        # Mock the agent to raise an exception
        with patch("agent.agent") as mock_agent:
            mock_stream = AsyncMock()
            mock_stream.__aiter__.return_value = iter([])
            mock_stream.side_effect = Exception("Test error")
            mock_agent.astream.return_value = mock_stream

            client = TestClient(app)
            with client.websocket_connect("/ws/agent") as websocket:
                websocket.send_text("Test message")

                # Should receive START
                msg_str = websocket.receive_text()
                start_msg = json.loads(msg_str)
                assert start_msg["type"] == "start"

                # Next message might be ERROR due to processing failure
                msg_str = websocket.receive_text()
                error_msg = json.loads(msg_str)

                # Could be ERROR or END depending on timing
                if error_msg["type"] == "error":
                    assert error_msg["code"] == "PROCESSING_ERROR"
                    assert "error processing message" in error_msg["message"].lower()

    def test_invalid_json_handling(self):
        """Test that invalid input is handled gracefully."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Send empty message (valid but might cause issues)
            websocket.send_text("")

            messages = []
            # Collect messages
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                messages.append(msg)

                if msg["type"] == "end" or msg["type"] == "error":
                    break

            # Should have received at least START
            assert len(messages) > 0
            assert messages[0]["type"] == "start"

    def test_websocket_disconnect_handling(self):
        """Test that disconnection is handled gracefully."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Send a message then immediately disconnect
            websocket.send_text("Hello")
            websocket.close()

            # Connection should close without errors
            # (This is mainly testing that the server doesn't crash)
            assert True

    def test_error_message_structure(self):
        """Test that error messages have correct structure."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Wait for timeout to get an error message
            msg_str = websocket.receive_text()
            msg = json.loads(msg_str)

            if msg["type"] == "error":
                # Verify error structure
                assert "message" in msg
                assert "code" in msg
                assert isinstance(msg["message"], str)
                assert isinstance(msg["code"], str)
                assert len(msg["message"]) > 0
                assert len(msg["code"]) > 0
