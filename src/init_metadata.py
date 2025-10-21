from core.db.sqlserver_client import SQLServerClient
from core.db.postgres_client import PostgresClient
from config import settings
from config.config_loader import load_server_configs


def sync_metadata():
    servers = load_server_configs()

    pg = PostgresClient(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB
    )
    pg.connect()

    for srv in servers:
        print(f"🔄 Syncing server: {srv['name']} ({srv['host']})")
        pg.insert_server_if_not_exists(
            name=srv["name"],
            host=srv["host"],
            port=srv["port"],
            username=srv["username"],
            password=srv["password"],
        )

    servers = pg.get_servers()
    message_errors = []

    for server in servers:
        server_id = server.get('id')
        server_name = server.get('name')
        host = server.get('host')
        port = server.get('port')
        username = server.get('username')
        enc_pwd = server.get('encrypted_password')

        sql = SQLServerClient(host, port, username, enc_pwd)
        try:
            sql.connect()
        except Exception as e:
            print(f"[ERROR] Cannot connect to SQL Server {server_name}: {e}")
            message_errors.append(f"[ERROR] Cannot connect to SQL Server {server_name}: {e}")
            continue

        databases = sql.discover_databases()
        print(f"[INFO] Found {len(databases)} databases")
        for db_name in databases:
            db_id = pg.insert_database_if_not_exists(server_id, db_name)
            schemas = sql.discover_schemas(db_name)
            for schema_name in schemas:
                sc_id = pg.insert_schema_if_not_exists(db_id, schema_name)
                tables = sql.discover_tables(db_name, schema_name)
                for table_name in tables:
                    tab_id = pg.insert_table_if_not_exists(sc_id, table_name)
                    columns = sql.discover_columns(db_name, schema_name, table_name)
                    pg.insert_columns_if_not_exists(tab_id, columns)


        sql.close()

    pg.commit()
    pg.close()
    if message_errors:
        return False, message_errors
    else:
        print("[INFO] Metadata sync completed successfully.")
        return True, message_errors

if __name__ == "__main__":
    sync_metadata()
