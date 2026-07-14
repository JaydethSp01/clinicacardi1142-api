"""CRUD generico server-side: /data/{entity} para cualquier entidad."""
from fastapi import APIRouter
from app import data_store
router = APIRouter()
@router.get("/data/{entity}")
async def listar(entity: str): return data_store.listar(entity)
@router.post("/data/{entity}")
async def crear(entity: str, body: dict): return data_store.crear(entity, body)
@router.put("/data/{entity}/{rid}")
async def actualizar(entity: str, rid: int, body: dict): return data_store.actualizar(entity, rid, body)
@router.delete("/data/{entity}/{rid}")
async def borrar(entity: str, rid: int): return data_store.borrar(entity, rid)
