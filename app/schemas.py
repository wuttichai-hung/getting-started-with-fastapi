from pydantic import BaseModel

class ItemBase(BaseModel):
    title: str
    description: str = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True