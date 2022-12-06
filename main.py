from fastapi import FastAPI, Depends
from uvicorn import run

from sqlalchemy.orm import Session

import models
import schemas
import database

app = FastAPI()


def get_db_session():
    """Create and yield DB session object."""
    db_session = database.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@app.get('/')
async def root() -> dict:
    """Only endpoint with simple JSON response."""
    return {'status': 'OK'}


@app.get('/products', response_model=schemas.Product)
async def get_products(db: Session = Depends(get_db_session)):
    """Return list of products."""
    return db.query(models.Product).all()


if __name__ == '__main__':
    run('main:app', host='0.0.0.0', port=80, log_level='info')
