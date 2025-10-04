set dotenv-load

env:
    cp .env.dist .env

lint:
    cd apps/backend && uv run ruff check --fix
    cd apps/backend && uv run ruff format .

setup:
    cd apps/backend && uv sync

run-server:
    cd apps/backend && uv run uvicorn main:app --host $SERVER_HOST --port $SERVER_PORT --workers 2 --log-level info

run-frontend:
    cd apps/frontend && npm run dev

run-client:
    wscat -c ws://$SERVER_HOST:$SERVER_PORT/ws/chat

docker-run-server:
    cd docker && docker compose up --build --force-recreate --remove-orphans

docker-run-client:
    wscat -c http://localhost:8080/ws/chat
