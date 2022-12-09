from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.orm import Session

from bcrypt import checkpw

from database import get_db_session
from models import User

security = HTTPBasic()


def login_required(credentials: HTTPBasicCredentials = Depends(security),
                   db: Session = Depends(get_db_session)):
    """Verify if valid credentials are provided in the requests (basic auth)."""
    user = db.query(User).filter(User.name == credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    is_pass_ok = checkpw(credentials.password.encode('utf8'), user.password)
    if not is_pass_ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
