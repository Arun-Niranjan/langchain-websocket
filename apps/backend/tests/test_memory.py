import json

from starlette.testclient import TestClient

from main import app


class TestSessionMemory:
    """Test session-based memory persistence."""

    def test_conversation_memory_within_session(self):
        """Test that the agent remembers previous messages in the same session."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # First message - establish context
            websocket.send_text("My name is Alice")

            # Wait for response to complete
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                if msg["type"] == "end":
                    break

            # Second message - reference previous context
            websocket.send_text("What is my name?")

            content_pieces = []
            # Collect the response
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "content_delta":
                    content_pieces.append(msg["delta"])

                if msg["type"] == "end":
                    break

            # The response should mention "Alice"
            full_response = "".join(content_pieces).lower()
            assert "alice" in full_response

    def test_memory_isolation_between_connections(self):
        """Test that different WebSocket connections have isolated memory."""
        client = TestClient(app)
        # First connection
        with client.websocket_connect("/ws/agent") as websocket1:
            websocket1.send_text("My name is Bob")

            while True:
                msg_str = websocket1.receive_text()
                msg = json.loads(msg_str)
                if msg["type"] == "end":
                    break

        # Second connection (different session)
        with client.websocket_connect("/ws/agent") as websocket2:
            websocket2.send_text("What is my name?")

            content_pieces = []
            while True:
                msg_str = websocket2.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "content_delta":
                    content_pieces.append(msg["delta"])

                if msg["type"] == "end":
                    break

            # The response should NOT mention "Bob" since it's a different session
            full_response = "".join(content_pieces).lower()
            # Agent should indicate it doesn't know (e.g., "don't know", "not sure")
            # or ask for clarification, but should not say "Bob"
            assert "bob" not in full_response

    def test_session_persists_across_multiple_exchanges(self):
        """Test that memory persists across multiple message exchanges."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Exchange 1: Set favorite color
            websocket.send_text("My favorite color is blue")
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                if msg["type"] == "end":
                    break

            # Exchange 2: Set favorite food
            websocket.send_text("My favorite food is pizza")
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                if msg["type"] == "end":
                    break

            # Exchange 3: Ask about first piece of information
            websocket.send_text("What is my favorite color?")
            content_pieces = []
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "content_delta":
                    content_pieces.append(msg["delta"])

                if msg["type"] == "end":
                    break

            # Should remember the color from earlier in the session
            full_response = "".join(content_pieces).lower()
            assert "blue" in full_response

    def test_tool_results_in_memory(self):
        """Test that tool call results are remembered in conversation history."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # First message - get transactions
            websocket.send_text("What are my transactions?")

            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)
                if msg["type"] == "end":
                    break

            # Second message - ask about transactions again
            # Should not need to call tool again (may use memory)
            websocket.send_text("How many transactions did you just show me?")

            content_pieces = []
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "content_delta":
                    content_pieces.append(msg["delta"])

                if msg["type"] == "end":
                    break

            # Should be able to answer based on previous tool call
            full_response = "".join(content_pieces)
            # Response should contain a number (2 transactions in mock data)
            assert any(char.isdigit() for char in full_response)
