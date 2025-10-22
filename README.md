# MCP Server

Model Context Protocol (MCP) is a framework designed to manage and standardize metadata across multiple database servers.

This project implements an MCP server that specifically supports Microsoft SQL Server environments, allowing you to:

- Connect to multiple SQL Server instances

- Handle multiple databases per server

- Handle multiple schemas per database

- Maintain a centralized metadata store in PostgreSQL

- Provide a scalable foundation for querying and managing schemas, tables, and columns across all connected servers

The goal of this project is to provide a generic, maintainable, and extensible MCP server that can serve as a backbone for multi-server, multi-database, multi-schema SQL Server environments.

_This project is containerized with Docker Compose, supports initialization scripts, and provides convenient commands via a Makefile._

## 🚀 Features

- Connect to one or more SQL Server instances (local or remote)

- Store metadata about servers, databases, schemas, tables, and columns in PostgreSQL

- Periodic metadata synchronization capability

- Redis caching support

- Fully containerized for local development and testing

- Ready for secret management integration (AWS/GCP/Azure)

## 📦 Project Structure
```bash
.
├── src/                  # Application source code
│   ├── app.py            # FastAPI entrypoint
│   ├── init_metadata.py  # Metadata initialization
│   ├── core/
│   │   ├── db/
│   │   │   ├── postgres_client.py
│   │   │   ├── mssql_client.py
│   │   │   └── orm/
│   │   └── utils/
│   │       └── crypto_utils.py
│   └── config/           # Configuration files (servers.yml)
├── sql/                  # SQL scripts for initializing databases
├── scripts/
│   └── init-db.sh        # Database seeding script
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.init       # For database initialization
├── Makefile
└── .env                  # Environment variables
```
## ⚙️ Prerequisites

- Docker ≥ 20.10

- Docker Compose ≥ 2.0

- Python ≥ 3.12 (inside container)

## 🛠 Environment Variables
```txt

All sensitive or environment-specific values should go in the .env file:

POSTGRES_USER=mcp_user
POSTGRES_PASSWORD=<YourPassword>
POSTGRES_DB=mcp_meta
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

SQLSERVER_HOST=sqlserver
SQLSERVER_PORT=1433
SQLSERVER_DB=master
SQLSERVER_USER=sa
SQLSERVER_PASSWORD=<YourPassword>

MCP_SERVER_PORT=8080

# Optional: Fernet key for encrypting server passwords
ENCRYPTION_KEY=<generated_fernet_key>

# Optional SQL Server passwords for metadata initialization
MSSQL_PASS_1=<YourPassword>
```
## 🐳 Docker Compose

The project runs four main services:

| Service |	Description |
|---------|-------------|
| mcp-server |	MCP FastAPI server, metadata sync, API endpoints |
| postgres |	PostgreSQL metadata store |
| redis |	Redis caching |
| sqlserver |	Local SQL Server for testing |
| init-db |	Database seeding script (runs once on startup) |

Start all services:
```bash
make build       # Build images
make up          # Start containers
```

Stop all services:
```bash
make down
```

Tail MCP server logs:
```bash
make logs
```
## 📝 Makefile Commands
| Command |	Description |
|---------|-------------|
| make build |	Build Docker images |
| make up |	Start all containers |
| make down |	Stop all containers |
| make restart |	Restart all containers and volumes |
| make logs |	Tail MCP server logs |
| make psql |	Open PostgreSQL interactive shell |
| make sqlcmd |	Open SQL Server interactive shell |
| make seed |	Run DB seeding (init-db.sh) |
| make init_metadata |	Run MCP metadata initialization |

## ⚡ Metadata Initialization

After starting containers, initialize the metadata store:
```bash
make init_metadata
```

This will:

- Load the servers.yml configuration (src/config/servers.yml)

- Encrypt server passwords via crypto_utils

- Insert servers into the servers table if they don’t exist

- Optionally, sync databases, schemas, tables, and columns for future phases

## 🔒 Password Encryption

Passwords stored in PostgreSQL are encrypted using Fernet.

- Generate a key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

- Store the key in .env as ENCRYPTION_KEY

## 🗓 High-Level Timeline / Roadmap

| Phase | Description | Deliverables | Status |
|-------|-------------|-------------|--------|
| ⚙️ **Phase 1** | Foundations & Environment Setup | Docker Compose, project scaffolding, config & secrets management | ✅ Completed |
| 🧩 **Phase 2** | Metadata Registry (PostgreSQL) | Schema design, ORM, metadata API, discovery job, health monitor, tagging | 2.1 Completed, 2.3 Completed, others Next |
| ⚡ **Phase 3** | Cache Layer (Redis) | Metadata cache, query result cache, invalidation, metrics | 🔜 Next |
| 🧠 **Phase 4** | Core Query Execution Engine | Query planner, connection manager, dispatcher, executor, result aggregator, normalizer, circuit breaker, observability | 🔜 Next |
| 🌐 **Phase 5** | MCP API Layer | API server, request validation, auth/ACL, streaming, error handling | 🔜 Next |
| 🧩 **Phase 6** | Observability & Admin Tools | Metrics, logging, tracing, admin UI, CLI tools | 🔜 Next |
| 🧪 **Phase 7** | Testing & QA | Unit, integration, load, fault injection, performance tuning | 🔜 Next |


## 💡 Tips

- Keep servers.yml in /config folder for portability and environment separation

- Use .env to override passwords or sensitive settings

- Use make restart to fully reset containers including volumes
