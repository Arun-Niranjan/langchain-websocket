# langchain-websocket

A simple [Starlette](https://www.starlette.io/) and react application that demonstrates [Langchain runnable streaming](https://python.langchain.com/docs/how_to/streaming/) with websocketsa and an agent with a dummy tool

## Setup
Install:
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [just](https://github.com/casey/just)
- [wscat](https://github.com/websockets/wscat)
and then run
```bash
just setup
```

## Environment variables
See .env.dist for what you need. Then run
```bash
just env
```
and populate your .env file.

## Running the chatbot
### Server
in one terminal, run
```bash
just run-server
```

you should then see something like:
```bash
uv run uvicorn main:app --host $SERVER_HOST --port $SERVER_PORT --workers 2
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
INFO:     Started parent process [1068812]
INFO:     Started server process [1068815]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Started server process [1068814]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

in another terminal, run
### Client
```bash
just run-client
```

and you should see something like:
```bash
wscat -c http://$SERVER_HOST:$SERVER_PORT/ws/chat
Connected (press CTRL+C to quit)
>
```

## Docker + Reverse Proxy
To build a docker network with Caddy as a reverse proxy behind localhost run
```bash
just docker-run-server
```
You can then chat with the webserver behind the proxy using
```bash
just docker-run-client
```

## React Front-End
whilst the docker server is running, run:
```bash
just run-frontend
```