from core.db.sqlserver_client import SQLServerClient
from core.db.postgres_client import PostgresClient
from core.utils.secrets_manager import get_secret
from config import settings

def sync_metadata():
    pg = PostgresClient(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB
    )
    pg.connect()

    servers = pg.get_servers()
    print(servers)
    for server_id, server_name, host, port, username, enc_pwd in servers:
        password = get_secret(enc_pwd)
        sql = SQLServerClient(host, port, username, password)
        try:
            sql.connect()
        except Exception as e:
            print(f"[ERROR] Cannot connect to SQL Server {server_name}: {e}")
            continue

        databases = sql.discover_databases()
        print(f"[INFO] Found {len(databases)} databases")
        for db_name in databases:
            db_id = pg.insert_database_if_not_exists(server_id, db_name)
            schemas = sql.discover_schemas(db_name)
            for schema_name in schemas:
                pg.insert_schema_if_not_exists(db_id, schema_name)
                print("[INFO] Inserting Schema.")

        sql.close()

    pg.commit()
    pg.close()
    print("[INFO] Metadata sync completed successfully.")


if __name__ == "__main__":
    sync_metadata()
