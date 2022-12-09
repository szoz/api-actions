from sqlalchemy import Column, Integer, String, BINARY

from database import Base


class Product(Base):
    """Product ORM model."""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Integer)


class User(Base):
    """User ORM model."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    password = Column(BINARY())
