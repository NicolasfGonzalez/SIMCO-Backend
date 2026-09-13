from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import List


class GreenhouseBase(BaseModel):
    name: str

class GreenhouseResponse(GreenhouseBase):
    id_greenhouse: UUID
    id_client: UUID

    model_config = ConfigDict(from_attributes=True)


class GreenhouseBasicResponse(BaseModel):
    id_greenhouse: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)

class GreenhouseResponse(BaseModel):
    id_greenhouse: UUID
    name: str
    id_client: UUID

    model_config = ConfigDict(from_attributes=True)

class GreenhouseListResponse(BaseModel):
    items: List[GreenhouseResponse] = []

    model_config = ConfigDict(from_attributes=True)