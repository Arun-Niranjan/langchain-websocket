from starlette.testclient import TestClient

from main import app


class TestWebSocketConnection:
    """Test WebSocket connection lifecycle."""

    path = "/ws/agent"

    def test_websocket_connect_accept(self):
        """Test that WebSocket connection is accepted."""
        client = TestClient(app)
        with client.websocket_connect(self.path) as websocket:
            # Connection should be established
            assert websocket is not None

    def test_websocket_disconnect(self):
        """Test that WebSocket can disconnect gracefully."""
        client = TestClient(app)
        with client.websocket_connect(self.path) as websocket:
            websocket.close()
            # Should close without errors

    def test_multiple_concurrent_connections(self):
        """Test that multiple WebSocket connections can coexist."""
        c1 = TestClient(app)
        c2 = TestClient(app)

        with c1.websocket_connect(self.path) as ws1, c2.websocket_connect(self.path) as ws2:
            # Both connections should be established
            assert ws1 is not None
            assert ws2 is not None
