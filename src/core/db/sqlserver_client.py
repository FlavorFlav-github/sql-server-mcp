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
        # Use three-part naming: database.sys.schemas
        query = f"SELECT name FROM [{database_name}].sys.schemas"
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    def discover_tables(self, database_name: str, schema_name: str):
        """Return a list of tables in the given database and schema."""
        cursor = self.conn.cursor()
        query = f"""
        SELECT TABLE_NAME 
        FROM [{database_name}].INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = ? AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        cursor.execute(query, schema_name)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def discover_columns(self, database_name: str, schema_name: str, table_name: str) -> str:
        """
        Returns a JSON string of column metadata for a specific table,
        including primary key and foreign key status, and a list of
        foreign key constraint details.
        """
        cursor = self.conn.cursor()

        query = f"""
        WITH PK_CTE AS (
            -- Find all Primary Key columns for the target table
            SELECT
                C.name AS COLUMN_NAME
            FROM
                [{database_name}].sys.objects T
            INNER JOIN
                [{database_name}].sys.columns C ON T.object_id = C.object_id
            INNER JOIN
                [{database_name}].sys.index_columns IC ON T.object_id = IC.object_id AND C.column_id = IC.column_id
            INNER JOIN
                [{database_name}].sys.indexes I ON IC.object_id = I.object_id AND IC.index_id = I.index_id
            WHERE
                T.is_ms_shipped = 0
                AND T.name = '{table_name}'
                AND SCHEMA_NAME(T.schema_id) = '{schema_name}'
                AND I.is_primary_key = 1
        ),
        FK_CTE AS (
            -- Find all Foreign Key columns and the referenced table/column
            SELECT
                COL_NAME(FK.parent_object_id, FKE.parent_column_id) AS COLUMN_NAME,
                CONCAT(
                    OBJECT_SCHEMA_NAME(FK.referenced_object_id), 
                    '.', 
                    OBJECT_NAME(FK.referenced_object_id), 
                    '(', 
                    COL_NAME(FK.referenced_object_id, FKE.referenced_column_id), 
                    ')'
                ) AS FK_REFERENCE
            FROM
                [{database_name}].sys.foreign_keys FK
            INNER JOIN
                [{database_name}].sys.foreign_key_columns FKE 
                    ON FK.object_id = FKE.constraint_object_id
            WHERE
                OBJECT_NAME(FK.parent_object_id) = '{table_name}'
                AND OBJECT_SCHEMA_NAME(FK.parent_object_id) = '{schema_name}'
        )
        SELECT
            C.COLUMN_NAME AS name,
            C.DATA_TYPE AS data_type,
            
            -- Use CHARACTER_MAXIMUM_LENGTH for strings, otherwise use NUMERIC_PRECISION
            CASE 
                WHEN C.CHARACTER_MAXIMUM_LENGTH IS NOT NULL THEN C.CHARACTER_MAXIMUM_LENGTH
                WHEN C.NUMERIC_PRECISION IS NOT NULL THEN C.NUMERIC_PRECISION
                ELSE NULL
            END AS max_length,
            
            -- Add NUMERIC_SCALE for decimal/numeric types
            C.NUMERIC_SCALE AS numeric_scale, 
        
            CASE WHEN C.IS_NULLABLE = 'YES' THEN 1 ELSE 0 END AS is_nullable,
            C.COLUMN_DEFAULT AS default_value,
            C.ORDINAL_POSITION AS ordinal_position,
        
            -- Primary Key check
            CASE WHEN PK.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END AS is_primary_key,
        
            -- Foreign Key check
            CASE WHEN FK.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END AS is_foreign_key,
        
            -- Foreign Key references (CSV-like list of references)
            STUFF((
                SELECT ',' + T2.FK_REFERENCE
                FROM FK_CTE T2
                WHERE T2.COLUMN_NAME = C.COLUMN_NAME
                FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(MAX)'), 1, 1, '') AS foreign_key_references
        
        FROM
            [{database_name}].INFORMATION_SCHEMA.COLUMNS AS C
        LEFT JOIN
            PK_CTE PK ON C.COLUMN_NAME = PK.COLUMN_NAME
        LEFT JOIN
            FK_CTE FK ON C.COLUMN_NAME = FK.COLUMN_NAME
        WHERE
            C.TABLE_SCHEMA = '{schema_name}'
            AND C.TABLE_NAME = '{table_name}'
        ORDER BY
            C.ORDINAL_POSITION
        FOR JSON PATH;
        """

        # Execute the query
        cursor.execute(query)

        # The result is a single row, single column containing the JSON string
        json_result = cursor.fetchone()[0]
        print(json_result)
        cursor.close()

        # The SQL query handles the JSON formatting, so just return the string
        return json_result