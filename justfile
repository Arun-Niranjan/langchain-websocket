set dotenv-load

env:
    cp .env.dist .env

lint:
    uv run ruff check --fix
    uv run ruff format .

setup:
    uv sync

run-server:
    uv run uvicorn main:app --host $SERVER_HOST --port $SERVER_PORT --workers 2 --log-level info

run-client:
    wscat -c http://$SERVER_HOST:$SERVER_PORT/ws/chat

docker-run-server:
    docker compose up --build --force-recreate

docker-run-client:
    wscat -c http://localhost:8080/ws/chat
