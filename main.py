from fastapi import FastAPI, Depends

from uvicorn import run

from sqlalchemy.orm import Session

import models
import schemas
from database import get_db_session
from auth import login_required

app = FastAPI()


@app.get('/')
async def root() -> dict:
    """Only endpoint with simple JSON response."""
    return {'status': 'OK'}


@app.get('/login', dependencies=[Depends(login_required)])
async def login():
    """Log into the API using basic auth."""
    return {'auth': 'OK'}


@app.get('/products', response_model=list[schemas.Product])
async def get_products(db: Session = Depends(get_db_session)):
    """Return list of products."""
    return db.query(models.Product).all()


if __name__ == '__main__':
    run('main:app', host='0.0.0.0', port=80, log_level='info')
