set dotenv-load

env:
    cp .env.dist .env

lint:
    cd apps/backend && uv run ruff check --fix
    cd apps/backend && uv run ruff format .

test:
    cd apps/backend && uv run --group test pytest -v

test-cov:
    cd apps/backend && uv run --group test pytest -v --cov=. --cov-report=term-missing

setup:
    cd apps/backend && uv sync
    cd apps/frontend && npm install

run-server:
    cd apps/backend && uv run uvicorn main:app --host $SERVER_HOST --port $SERVER_PORT --workers 2 --log-level info

run-frontend:
    cd apps/frontend && npm run dev

run-client:
    wscat -c ws://$SERVER_HOST:$SERVER_PORT/ws/agent

docker-run-server:
    cd docker && docker compose up --build --force-recreate --remove-orphans

docker-run-client:
    wscat -c http://localhost:8080/ws/agent
