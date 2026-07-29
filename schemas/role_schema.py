from pydantic import BaseModel


class RoleOut(BaseModel):
    id_role: int
    name: str

    class Config:
        orm_mode = True