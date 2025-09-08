set dotenv-load

env:
    cp .env.dist .env

lint:
    uv run ruff check --fix
    uv run ruff format .

setup:
    uv sync

run-server:
    uv run uvicorn main:app --host $SERVER_HOST --port $SERVER_PORT --workers 2

run-client:
    wscat -c http://$SERVER_HOST:$SERVER_PORT/ws/chat

docker-build:
    docker build -t langchain-websocket-server .

docker-run:
    docker run -p $SERVER_PORT:8000 --env-file .env langchain-websocket-server
