#!/usr/bin/env bash
set -e

echo "=== [MCP INIT] Waiting for services to become ready... ==="

# Wait for Postgres (using service name, not container name)
until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c '\q' > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done
echo "PostgreSQL is ready!"

# Wait for SQL Server (using service name, not container name)
until /opt/mssql-tools18/bin/sqlcmd -S "${SQLSERVER_HOST},${SQLSERVER_PORT}" -U "${SQLSERVER_USER}" -P "${SQLSERVER_PASSWORD}" -Q "SELECT 1" -C > /dev/null 2>&1; do
  echo "Waiting for SQL Server..."
  sleep 5
done
echo "SQL Server is ready!"

echo "=== [MCP INIT] Creating metadata schema in PostgreSQL ==="
PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -f /sql/postgres/init_metadata.sql

echo "=== [MCP INIT] Setting up SQL Server structure ==="
/opt/mssql-tools18/bin/sqlcmd -S "${SQLSERVER_HOST},${SQLSERVER_PORT}" -U "${SQLSERVER_USER}" -P "${SQLSERVER_PASSWORD}" -C -i /sql/sqlserver/create_databases.sql
/opt/mssql-tools18/bin/sqlcmd -S "${SQLSERVER_HOST},${SQLSERVER_PORT}" -U "${SQLSERVER_USER}" -P "${SQLSERVER_PASSWORD}" -C -i /sql/sqlserver/create_schemas.sql
/opt/mssql-tools18/bin/sqlcmd -S "${SQLSERVER_HOST},${SQLSERVER_PORT}" -U "${SQLSERVER_USER}" -P "${SQLSERVER_PASSWORD}" -C -i /sql/sqlserver/seed_data.sql

echo "=== [MCP INIT] Initialization complete! ==="