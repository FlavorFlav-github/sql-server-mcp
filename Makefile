# === Makefile for MCP Project ===

APP_NAME = mcp-server
DOCKER_COMPOSE = docker compose

# Default target
.PHONY: help
help:
	@echo ""
	@echo "MCP Server Makefile commands:"
	@echo "  make build         Build Docker images"
	@echo "  make up            Start all containers"
	@echo "  make down          Stop all containers"
	@echo "  make restart       Restart all containers"
	@echo "  make logs          Tail logs from MCP server"
	@echo "  make psql          Open Postgres shell"
	@echo "  make sqlcmd        Open SQL Server shell"
	@echo "  make seed          Run init-db.sh (seed DBs)"
	@echo ""

.PHONY: build
build:
	$(DOCKER_COMPOSE) build

.PHONY: up_build
up:
	$(DOCKER_COMPOSE) --profile app up --build

.PHONY: up
up:
	$(DOCKER_COMPOSE) --profile app up

.PHONY: down
down:
	$(DOCKER_COMPOSE) --profile app down

.PHONY: restart
restart:
	$(DOCKER_COMPOSE) --profile app down -v
	$(DOCKER_COMPOSE) --profile app up -d

.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f $(APP_NAME)

.PHONY: psql
psql:
	@docker exec -it postgres psql -U mcp_user -d mcp_meta

.PHONY: sqlcmd
sqlcmd:
	@docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' -C

.PHONY: init_db
seed:
	@set -a && . .env && set +a && ./scripts/init-db.sh

.PHONY: init_metadata
init_metadata:
	@echo "=== Running MCP metadata initialization ==="
	@docker exec -it $(APP_NAME) python -m src.init_metadata