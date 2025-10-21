import json
from typing import List, Dict, Any, Optional

import psycopg2
from psycopg2.extras import execute_values, RealDictCursor

from core.utils.crypto_utils import CryptoUtils

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

    # ---------------------------------------------------------------------
    # Generic query runner
    # ---------------------------------------------------------------------

    def _execute(self, query: str, params: Optional[tuple] = None, fetch: bool = True) -> Optional[
        List[Dict[str, Any]]]:
        """
        Execute a SQL query against the metadata database.
        If `fetch` is True, returns the results as a list of dicts.
        """
        if not self.conn:
            self.connect()

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            else:
                self.conn.commit()
                return None

    # ------------------------
    # Methods for servers metadata table interaction
    # ------------------------

    def insert_server_if_not_exists(self, name, host, port, username, password):
        """Insert a database entry if not already present."""
        with self.conn.cursor() as cur:
            cry = CryptoUtils()
            cur.execute("""
                INSERT INTO servers (name, host, port, username, encrypted_password)
                SELECT %s, %s, %s, %s, %s 
                WHERE NOT EXISTS (
                    SELECT 1 FROM servers WHERE name=%s AND host=%s
                );
            """, (name, host, port, username, cry.encrypt(password), name, host))

    def get_servers(self) -> List[Dict[str, Any]]:
        """Return all registered SQL Server instances."""
        query = "SELECT id, name, host, port, username, encrypted_password FROM servers ORDER BY id;"
        servers = self._execute(query)
        cry = CryptoUtils()
        for server in servers:
            server['encrypted_password'] = cry.decrypt(server['encrypted_password'])
        return servers

    # ------------------------
    # Methods for databases metadata table interaction
    # ------------------------

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

    def get_databases(self, server_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return databases; if server_id is None, return all."""
        if server_id is not None:
            query = """
                SELECT id, name, server_id, created_at
                FROM databases
                WHERE server_id = %s
                ORDER BY name;
            """
            params = (server_id,)
        else:
            query = """
                SELECT id, name, server_id, created_at
                FROM databases
                ORDER BY name;
            """
            params = None
        return self._execute(query, params)

    # ------------------------
    # Methods for scemas metadata table interaction
    # ------------------------

    def insert_schema_if_not_exists(self, database_id, schema_name):
        """Insert a schema entry if not already present."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO schemas (database_id, name)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM schemas WHERE database_id=%s AND name=%s
                )
                RETURNING id;
            """, (database_id, schema_name, database_id, schema_name))

            result = cur.fetchone()
            if result:
                return result[0]
            else:
                # Already exists, fetch id
                cur.execute("SELECT id FROM schemas WHERE database_id=%s AND name=%s;", (database_id, schema_name))
                return cur.fetchone()[0]

    def get_schemas(self, database_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return schemas; if database_id is None, return all."""
        if database_id is not None:
            query = """
                SELECT id, name, database_id, created_at
                FROM schemas
                WHERE database_id = %s
                ORDER BY name;
            """
            params = (database_id,)
        else:
            query = """
                SELECT id, name, database_id, created_at
                FROM schemas
                ORDER BY name;
            """
            params = None
        return self._execute(query, params)

    # ------------------------
    # Methods for tables metadata table interaction
    # ------------------------

    def insert_table_if_not_exists(self, schema_id: int, table_name: str):
        """Light sync - just record table existence"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tables (schema_id, name)
                VALUES (%s, %s)
                ON CONFLICT (schema_id, name) DO UPDATE 
                SET created_at = NOW()
                RETURNING id;
                """,
                (schema_id, table_name)
            )

            result = cur.fetchone()
            if result:
                return result[0]
            else:
                # Already exists, fetch id
                cur.execute("SELECT id FROM schemas WHERE schema_id=%s AND name=%s;", (schema_id, table_name))
                return cur.fetchone()[0]

    def get_tables(self, schema_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return tables; if schema_id is None, return all."""
        if schema_id is not None:
            query = """
                SELECT id, name, schema_id, created_at
                FROM tables
                WHERE schema_id = %s
                ORDER BY name;
            """
            params = (schema_id,)
        else:
            query = """
                SELECT id, name, schema_id, created_at
                FROM tables
                ORDER BY name;
            """
            params = None
        return self._execute(query, params)

    # ------------------------
    # Methods for columns metadata table interaction
    # ------------------------

    def insert_columns_if_not_exists(self, table_id: int, columns_json_str: str):
        """
        Inserts or updates column metadata for a specific table using data
        from the discover_columns_json method's output.
        """
        # 1. Parse the JSON string into a Python list of dictionaries
        try:
            columns_data: List[Dict[str, Any]] = json.loads(columns_json_str)
        except json.JSONDecodeError:
            print("Error: Could not decode JSON string.")
            return 0

        inserted_count = 0

        with self.conn.cursor() as cur:
            # Prepare the base SQL statement
            sql_statement = """
            INSERT INTO columns (
                table_id, 
                name, 
                data_type, 
                max_length, 
                is_nullable, 
                is_primary_key, 
                is_foreign_key, 
                default_value, 
                ordinal_position
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (table_id, name) DO UPDATE 
            SET 
                data_type = EXCLUDED.data_type,
                max_length = EXCLUDED.max_length,
                is_nullable = EXCLUDED.is_nullable,
                is_primary_key = EXCLUDED.is_primary_key,
                is_foreign_key = EXCLUDED.is_foreign_key,
                default_value = EXCLUDED.default_value,
                ordinal_position = EXCLUDED.ordinal_position,
                created_at = NOW() -- optional: update timestamp to reflect sync
            """

            # 2. Iterate and execute the upsert for each column
            for column in columns_data:
                # Prepare the values tuple
                values = (
                    table_id,
                    column['name'],
                    column['data_type'],
                    column.get('max_length', None),
                    bool(column['is_nullable']),  # Convert 0/1 to boolean
                    bool(column['is_primary_key']),  # Convert 0/1 to boolean
                    bool(column['is_foreign_key']),  # Convert 0/1 to boolean
                    column.get('default_value'),  # Use .get() in case it's null
                    column['ordinal_position']
                )

                cur.execute(sql_statement, values)
                inserted_count += cur.rowcount  # Keep track of rows inserted/updated

        # Commit transaction outside the cursor block (assuming self.conn is set to autocommit=False)
        self.conn.commit()

        return inserted_count

    def get_columns(self, table_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return columns; if table_id is None, return all."""
        if table_id is not None:
            query = """
                SELECT
                    id, name, data_type, max_length, is_nullable,
                    is_primary_key, is_foreign_key, default_value,
                    ordinal_position, table_id, created_at
                FROM columns
                WHERE table_id = %s
                ORDER BY ordinal_position;
            """
            params = (table_id,)
        else:
            query = """
                SELECT
                    id, name, data_type, max_length, is_nullable,
                    is_primary_key, is_foreign_key, default_value,
                    ordinal_position, table_id, created_at
                FROM columns
                ORDER BY table_id, ordinal_position;
            """
            params = None
        return self._execute(query, params)

    # ---------------------------------------------------------------------
    # Utility for testing / debugging
    # ---------------------------------------------------------------------

    def reset_metadata(self):
        self._execute("DROP TABLE IF EXISTS columns;")
        self._execute("DROP TABLE IF EXISTS tables;")
        self._execute("DROP TABLE IF EXISTS schemas;")
        self._execute("DROP TABLE IF EXISTS databases;")
        self._execute("DROP TABLE IF EXISTS servers;")

    def ping(self) -> bool:
        """Check if the PostgreSQL connection is alive."""
        try:
            if not self.conn:
                self.connect()
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1;")
            return True
        except Exception:
            return False

    def commit(self):
        if self.conn:
            self.conn.commit()