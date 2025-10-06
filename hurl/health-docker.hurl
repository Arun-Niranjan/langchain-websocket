# Health check for dockerized server (behind Caddy)
# Run with: hurl health-docker.hurl
GET http://localhost:8080/health

HTTP 200
[Asserts]
jsonpath "$.status" == "ok"
