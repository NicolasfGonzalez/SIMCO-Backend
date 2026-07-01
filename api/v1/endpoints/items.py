from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter()

@router.get("/", response_model=List[ItemResponse])
def read_items():
    # Lógica genérica de consulta simulada
    return [{"id": 1, "title": "Elemento Base", "description": "Plantilla genérica"}]

@router.post("/", response_model=ItemResponse)
def create_item(item_in: ItemCreate):
    # Lógica genérica de creación simulada
    return {"id": 2, **item_in.model_dump()}