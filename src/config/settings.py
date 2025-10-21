from core.utils.secrets_manager import get_secret

POSTGRES_HOST = get_secret("POSTGRES_HOST")
POSTGRES_PORT = get_secret("POSTGRES_PORT")
POSTGRES_USER = get_secret("POSTGRES_USER")
POSTGRES_PASSWORD = get_secret("POSTGRES_PASSWORD")
POSTGRES_DB = get_secret("POSTGRES_DB")
MCP_SERVER_PORT = int(get_secret("MCP_SERVER_PORT", 8080))
MCP_SERVER_HOST = get_secret("MCP_SERVER_HOST")
PASSWORD_ENCRYPTION_KEY = get_secret("PASSWORD_ENCRYPTION_KEY")