from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any

from core.db.postgres_client import PostgresClient
from config import settings
from init_metadata import sync_metadata

router = APIRouter(prefix="/metadata", tags=["Metadata"])

# Instantiate the client (adjust credentials for your docker-compose env)
pg = PostgresClient(
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    dbname=settings.POSTGRES_DB
)


@router.get("/servers", response_model=List[Dict[str, Any]])
def get_servers():
    """Return all registered servers."""
    try:
        return pg.get_servers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/databases", response_model=List[Dict[str, Any]])
def get_databases():
    """Return all databases for a given server."""
    try:
        return pg.get_databases()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/servers/{server_id}/databases", response_model=List[Dict[str, Any]])
def get_databases_for_server(server_id: int):
    """Return all databases for a given server."""
    try:
        return pg.get_databases(server_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schemas", response_model=List[Dict[str, Any]])
def get_schemas():
    """Return all schemas for a given database."""
    try:
        return pg.get_schemas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/databases/{database_id}/schemas", response_model=List[Dict[str, Any]])
def get_schemas_for_database(database_id: int):
    """Return all schemas for a given database."""
    try:
        return pg.get_schemas(database_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables", response_model=List[Dict[str, Any]])
def get_tables():
    """Return all tables for a given schema."""
    try:
        return pg.get_tables()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schemas/{schema_id}/tables", response_model=List[Dict[str, Any]])
def get_tables_for_schema(schema_id: int):
    """Return all tables for a given schema."""
    try:
        return pg.get_tables(schema_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{table_id}/columns", response_model=List[Dict[str, Any]])
def get_columns(table_id: int):
    """Return all columns for a given table."""
    try:
        return pg.get_columns(table_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resync", response_model=List[Dict[str, Any]])
def get_columns():
    """Return all columns for a given table."""
    try:
        res, msgs = sync_metadata()
        if res:
            return JSONResponse(content={"message": "Resync completed successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message": f"Resync completed with warnings : \n {msgs}"}, status_code=304)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))