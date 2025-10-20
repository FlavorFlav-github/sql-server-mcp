import psycopg2
from psycopg2.extras import execute_values

class PostgresClient:
    """
    Generic PostgreSQL client for metadata management.
    """

    def __init__(self, host: str, port: int, user: str, password: str, dbname: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
        )

    def close(self):
        if self.conn:
            self.conn.close()

    # ------------------------
    # Methods for init metadata
    # ------------------------

    def get_servers(self):
        """Return all registered SQL Servers."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name, host, port, username, encrypted_password FROM servers;")
            return cur.fetchall()

    def insert_database_if_not_exists(self, server_id, db_name):
        """Insert a database entry if not already present."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO databases (server_id, name)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM databases WHERE server_id=%s AND name=%s
                )
                RETURNING id;
            """, (server_id, db_name, server_id, db_name))
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                # Already exists, fetch id
                cur.execute("SELECT id FROM databases WHERE server_id=%s AND name=%s;", (server_id, db_name))
                return cur.fetchone()[0]

    def insert_schema_if_not_exists(self, database_id, schema_name):
        """Insert a schema entry if not already present."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO schemas (database_id, name)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM schemas WHERE database_id=%s AND name=%s
                );
            """, (database_id, schema_name, database_id, schema_name))

    def commit(self):
        if self.conn:
            self.conn.commit()