# === Base image ===
FROM python:3.12-slim AS base

# === Environment ===
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src"

WORKDIR /app

# === System deps ===
# install msodbcsql18, ODBC libs, and build tools
RUN apt-get update && \
    apt-get install -y curl gnupg ca-certificates apt-transport-https unixodbc-dev gcc g++ && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

# === Python deps ===
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# === Copy source code ===
COPY src ./src
COPY sql ./sql

EXPOSE 8080

# === Default command ===
# You can override CMD in docker-compose to run init_metadata instead.
CMD ["python", "-m", "app"]