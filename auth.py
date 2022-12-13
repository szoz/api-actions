from os import environ
from time import time
from secrets import token_hex

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from bcrypt import checkpw
from jwt import encode, decode
from jwt.exceptions import InvalidTokenError

from database import get_db_session
from models import User

JWT_SECRET = environ.get("JWT_SECRET", token_hex(24))
JWT_ALGORITHM = "HS256"
JWT_EXPIRE = 15 * 60

security_basic = HTTPBasic()
security_token = HTTPBearer()


def login_required(
    credentials: HTTPBasicCredentials = Depends(security_basic), db: Session = Depends(get_db_session)
) -> None:
    """Verify if valid credentials are provided in the request (basic auth)."""
    user = db.query(User).filter(User.name == credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    is_pass_ok = checkpw(credentials.password.encode("utf8"), user.password)
    if not is_pass_ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def generate_token_payload_response(credentials: HTTPBasicCredentials = Depends(security_basic)) -> dict:
    """Generate JWT for given user credentials"""
    payload = {"user": credentials.username, "exp": time() + JWT_EXPIRE}
    token = encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {"access_token": token, "expires_in": JWT_EXPIRE}


def token_required(credentials: HTTPAuthorizationCredentials = Depends(security_token)) -> None:
    """Verify if valid token is provided in the request."""
    token = credentials.credentials
    try:
        decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
