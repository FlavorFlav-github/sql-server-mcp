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

-- ==============================
-- Optional: Seed initial server entries
-- ==============================
INSERT INTO servers (name, host, port, username, encrypted_password)
SELECT 'local_sqlserver', 'sqlserver', 1433, 'sa', 'YourStrong!Passw0rd'
WHERE NOT EXISTS (SELECT 1 FROM servers WHERE name='local_sqlserver');
