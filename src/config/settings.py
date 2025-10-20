from core.utils.secrets_manager import get_secret

POSTGRES_HOST = get_secret("POSTGRES_HOST")
POSTGRES_PORT = get_secret("POSTGRES_PORT")
POSTGRES_USER = get_secret("POSTGRES_USER")
POSTGRES_PASSWORD = get_secret("POSTGRES_PASSWORD")
POSTGRES_DB = get_secret("POSTGRES_DB")