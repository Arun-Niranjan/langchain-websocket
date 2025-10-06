import json

from starlette.testclient import TestClient

from main import app


class TestContentStreaming:
    """Test content streaming and accumulation."""

    def test_accumulated_content_grows(self):
        """Test that accumulated content in CONTENT_DELTA grows monotonically."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.send_text("Tell me about financial transactions")

            content_deltas = []
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "content_delta":
                    content_deltas.append(msg)

                if msg["type"] == "end":
                    break

            # If we got content deltas, verify accumulation
            if len(content_deltas) > 1:
                for i in range(1, len(content_deltas)):
                    prev_accumulated = content_deltas[i - 1]["accumulated"]
                    curr_accumulated = content_deltas[i]["accumulated"]

                    # Current should be longer or equal
                    assert len(curr_accumulated) >= len(prev_accumulated)

                    # Current should start with previous (monotonic growth)
                    assert curr_accumulated.startswith(prev_accumulated)

    def test_delta_plus_previous_equals_accumulated(self):
        """Test that each delta added to previous accumulated equals current accumulated."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.send_text("Explain financial transactions")

            content_deltas = []
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "content_delta":
                    content_deltas.append(msg)

                if msg["type"] == "end":
                    break

            # Verify relationship between delta and accumulated
            if len(content_deltas) > 0:
                # First delta's accumulated should equal its delta
                first = content_deltas[0]
                assert first["accumulated"] == first["delta"]

                # Each subsequent accumulated should be previous + delta
                for i in range(1, len(content_deltas)):
                    prev = content_deltas[i - 1]
                    curr = content_deltas[i]

                    expected_accumulated = prev["accumulated"] + curr["delta"]
                    assert curr["accumulated"] == expected_accumulated

    def test_content_complete_matches_final_accumulated(self):
        """Test that CONTENT_COMPLETE content matches final accumulated from deltas."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.send_text("What are financial transactions?")

            content_deltas = []
            content_complete = None

            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "content_delta":
                    content_deltas.append(msg)

                if msg["type"] == "content_complete":
                    content_complete = msg

                if msg["type"] == "end":
                    break

            # If we had streaming content
            if len(content_deltas) > 0 and content_complete is not None:
                final_accumulated = content_deltas[-1]["accumulated"]
                complete_content = content_complete["content"]

                # Should match
                assert final_accumulated == complete_content

    def test_non_empty_deltas(self):
        """Test that content deltas are non-empty strings."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.send_text("Describe transactions")

            content_deltas = []
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "content_delta":
                    content_deltas.append(msg)

                if msg["type"] == "end":
                    break

            # All deltas should be non-empty
            for delta_msg in content_deltas:
                assert isinstance(delta_msg["delta"], str)
                assert len(delta_msg["delta"]) > 0
                assert isinstance(delta_msg["accumulated"], str)
                assert len(delta_msg["accumulated"]) > 0

    def test_streaming_provides_incremental_updates(self):
        """Test that streaming provides incremental updates rather than sending everything at once."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.send_text("Explain what financial transactions are in detail")

            content_deltas = []
            while True:
                msg_str = websocket.receive_text()
                msg = json.loads(msg_str)

                if msg["type"] == "content_delta":
                    content_deltas.append(msg)

                if msg["type"] == "end":
                    break

            # Should have multiple deltas for streaming (not just one big chunk)
            # This verifies that content is actually being streamed
            if len(content_deltas) > 0:
                # At least for longer responses, we should see multiple deltas
                # (This is a heuristic - may vary based on LLM response)
                total_length = len(content_deltas[-1]["accumulated"])
                if total_length > 50:  # For longer responses
                    # Should have more than 1 delta
                    assert len(content_deltas) > 1
