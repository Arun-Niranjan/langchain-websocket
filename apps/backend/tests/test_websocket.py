from starlette.testclient import TestClient

from main import app


class TestWebSocketConnection:
    """Test WebSocket connection lifecycle."""

    def test_websocket_connect_accept(self):
        """Test that WebSocket connection is accepted."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            # Connection should be established
            assert websocket is not None

    def test_websocket_disconnect(self):
        """Test that WebSocket can disconnect gracefully."""
        client = TestClient(app)
        with client.websocket_connect("/ws/agent") as websocket:
            websocket.close()
            # Should close without errors

    def test_multiple_concurrent_connections(self):
        """Test that multiple WebSocket connections can coexist."""
        client1 = TestClient(app)
        client2 = TestClient(app)

        with client1.websocket_connect("/ws/agent") as ws1:
            with client2.websocket_connect("/ws/agent") as ws2:
                # Both connections should be established
                assert ws1 is not None
                assert ws2 is not None
