from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    price: str

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    access_token: str
    expires_in: int


class ErrorMessage(BaseModel):
    detail: str
