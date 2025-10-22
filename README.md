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

|Service |	Description |
|mcp-server |	MCP FastAPI server, metadata sync, API endpoints |
|postgres |	PostgreSQL metadata store |
|redis |	Redis caching |
|sqlserver |	Local SQL Server for testing |
|init-db |	Database seeding script (runs once on startup) |

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
|Command |	Description |
|make build |	Build Docker images |
|make up |	Start all containers |
|make down |	Stop all containers |
|make restart |	Restart all containers and volumes |
|make logs |	Tail MCP server logs |
|make psql |	Open PostgreSQL interactive shell |
|make sqlcmd |	Open SQL Server interactive shell |
|make seed |	Run DB seeding (init-db.sh) |
|make init_metadata |	Run MCP metadata initialization |
⚡ Metadata Initialization

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

## 📌 Next Steps / Phases

Phase 2.2: ORM layer with SQLAlchemy + Alembic migrations

Phase 2.4: API endpoints via FastAPI for CRUD on metadata

Phase 3: Multi-server multi-database introspection

Phase 4: Redis caching for metadata queries

Phase 5: Secret manager integration (AWS/GCP/Azure)

## 💡 Tips

- Keep servers.yml in /config folder for portability and environment separation

- Use .env to override passwords or sensitive settings

- Use make restart to fully reset containers including volumes
