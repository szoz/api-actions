from fastapi import FastAPI, Depends

from uvicorn import run

from sqlalchemy.orm import Session

import models
import schemas
from database import get_db_session
from auth import login_required, generate_token_payload_response, token_required

app = FastAPI()


@app.get("/")
async def root() -> dict:
    """Only endpoint with simple JSON response."""
    return {"status": "OK"}


@app.post(
    "/login",
    dependencies=[Depends(login_required)],
    response_model=schemas.TokenData,
    responses={401: {"model": schemas.ErrorMessage}},
)
async def login(token_data: str = Depends(generate_token_payload_response)):
    """Log into the API using basic auth."""
    return token_data


@app.get(
    "/products",
    dependencies=[Depends(token_required)],
    response_model=list[schemas.Product],
    responses={401: {"model": schemas.ErrorMessage}, 403: {"model": schemas.ErrorMessage}},
)
async def get_products(db: Session = Depends(get_db_session)):
    """Return list of products."""
    return db.query(models.Product).all()


if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=80, log_level="info")
