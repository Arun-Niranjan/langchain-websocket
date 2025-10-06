import json
import time

import pytest
from starlette.testclient import TestClient

from main import app

@pytest.mark.skip
class TestInactivityTimeout:
    """Test 15-second inactivity timeout behavior."""

    @pytest.mark.timeout(20)
    def test_timeout_after_15_seconds(self):
        """Test that connection times out after 15 seconds without user message."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Don't send any message, just wait
            # Should receive TIMEOUT error after ~15 seconds

            msg_str = websocket.receive_text()
            msg = json.loads(msg_str)

            # Should be an error message
            assert msg["type"] == "error"
            assert msg["code"] == "TIMEOUT"
            assert "inactivity" in msg["message"].lower()

    @pytest.mark.timeout(20)
    def test_connection_closes_after_timeout(self):
        """Test that WebSocket connection closes after timeout error."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Wait for timeout
            msg_str = websocket.receive_text()
            msg = json.loads(msg_str)

            assert msg["type"] == "error"
            assert msg["code"] == "TIMEOUT"

            # Connection should close
            # Trying to receive again should raise an exception or return close frame
            with pytest.raises(Exception):
                websocket.receive_text()

    def test_no_timeout_with_active_conversation(self):
        """Test that timeout doesn't occur during active conversation."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Send a message
            websocket.send_text("Hello")

            # Collect response (should complete before timeout)
            messages = []
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                messages.append(msg)

                if msg["type"] == "end":
                    break
                if msg["type"] == "error" and msg["code"] == "TIMEOUT":
                    pytest.fail("Timeout occurred during active conversation")

            # Should have completed successfully
            assert len(messages) > 0
            assert messages[-1]["type"] == "end"

    def test_timeout_resets_between_messages(self):
        """Test that timeout timer resets with each new user message."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Send first message
            websocket.send_text("First message")

            # Wait for response
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                if msg["type"] == "end":
                    break

            # Wait ~10 seconds (less than timeout)
            time.sleep(10)

            # Send second message (should reset timeout)
            websocket.send_text("Second message")

            # Should get response without timeout
            messages = []
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                messages.append(msg)

                if msg["type"] == "end":
                    break
                if msg["type"] == "error" and msg["code"] == "TIMEOUT":
                    pytest.fail(
                        "Timeout occurred after sending second message"
                    )

            # Should complete successfully
            assert messages[-1]["type"] == "end"
