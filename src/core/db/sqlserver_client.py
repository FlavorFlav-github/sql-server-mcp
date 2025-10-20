import pyodbc

class SQLServerClient:
    """
    Generic SQL Server client for connecting, discovering databases and schemas.
    """

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn = None

    def connect(self):
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.host},{self.port};"
            f"UID={self.username};PWD={self.password};"
            f"Encrypt=no;"
        )
        self.conn = pyodbc.connect(conn_str, autocommit=True)

    def close(self):
        if self.conn:
            self.conn.close()

    def discover_databases(self):
        """Return a list of non-system databases."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE name NOT IN ('master','tempdb','model','msdb');")
        return [row[0] for row in cursor.fetchall()]

    def discover_schemas(self, database_name: str):
        """Return a list of schemas in the given database."""
        cursor = self.conn.cursor()
        cursor.execute(f"USE [{database_name}]; SELECT name FROM sys.schemas;")
        return [row[0] for row in cursor.fetchall()]