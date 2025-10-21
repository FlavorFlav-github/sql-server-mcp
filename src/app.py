from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from config.settings import MCP_SERVER_PORT, MCP_SERVER_HOST
from api.metadata_api import router, pg

app = FastAPI()
app.include_router(router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup/shutdown lifecycle for resources."""
    print("🚀 Connecting to PostgreSQL metadata store...")
    try:
        pg.connect()
        print("✅ PostgreSQL connected.")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")

    yield  # ← FastAPI will handle requests during this block

    print("🧹 Closing PostgreSQL connection...")
    pg.close()
    print("✅ PostgreSQL connection closed.")

@app.get("/")
def root():
    return {"status": "running"}

if __name__ == "__main__":
    host = MCP_SERVER_HOST
    port = MCP_SERVER_PORT
    uvicorn.run("src.app:app", host=host, port=port, reload=False)