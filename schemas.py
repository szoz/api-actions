from pydantic import BaseModel


class Product(BaseModel):
    """Product pydantic model."""
    id: int
    name: str
    price: str

    class Config:
        orm_mode = True
