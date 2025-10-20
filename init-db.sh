#!/usr/bin/env bash
set -e

echo "=== [MCP INIT] Waiting for services to become ready... ==="

# Wait for Postgres
until docker exec postgres pg_isready -U mcp_user > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Wait for SQL Server
until docker exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' -Q "SELECT 1" -C > /dev/null 2>&1; do
  echo "Waiting for SQL Server..."
  sleep 5
done

echo "=== [MCP INIT] Creating metadata schema in PostgreSQL ==="
docker exec -i postgres psql -U mcp_user -d mcp_meta < ./sql/postgres/init_metadata.sql

echo "=== [MCP INIT] Setting up SQL Server structure ==="
docker exec -i sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' -C -i /sql/sqlserver/create_databases.sql
docker exec -i sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' -C -i /sql/sqlserver/create_schemas.sql
docker exec -i sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' -C -i /sql/sqlserver/seed_data.sql

echo "=== [MCP INIT] Initialization complete! ==="