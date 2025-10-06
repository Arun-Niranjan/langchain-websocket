# Health check for local server
# Run with: hurl health-local.hurl
GET http://127.0.0.1:3000/health

HTTP 200
[Asserts]
jsonpath "$.status" == "ok"
