-- ==============================
-- Servers table
-- ==============================
CREATE TABLE IF NOT EXISTS servers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INT NOT NULL,
    username VARCHAR(100) NOT NULL,
    encrypted_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- Databases table
-- ==============================
CREATE TABLE IF NOT EXISTS databases (
    id SERIAL PRIMARY KEY,
    server_id INT REFERENCES servers(id),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- Schemas table
-- ==============================
CREATE TABLE IF NOT EXISTS schemas (
    id SERIAL PRIMARY KEY,
    database_id INT REFERENCES databases(id),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tables in each schema
CREATE TABLE IF NOT EXISTS tables (
    id SERIAL PRIMARY KEY,
    schema_id INTEGER REFERENCES schemas(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(schema_id, name)
);

-- Columns for each table
CREATE TABLE IF NOT EXISTS columns (
    id SERIAL PRIMARY KEY,
    table_id INTEGER REFERENCES tables(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    max_length INTEGER,
    is_nullable BOOLEAN DEFAULT true,
    is_primary_key BOOLEAN DEFAULT false,
    is_foreign_key BOOLEAN DEFAULT false,
    default_value TEXT,
    ordinal_position INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(table_id, name)
);

-- ==============================
-- Query Logs table
-- ==============================
CREATE TABLE IF NOT EXISTS query_logs (
    id SERIAL PRIMARY KEY,
    query_text TEXT,
    target_scope JSONB,
    execution_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);