from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from os import getenv
from dotenv import load_dotenv
from fastapi import Cookie, Depends, HTTPException
import database
from models.user import User as UserModel

load_dotenv(override=False)

SECRET_KEY = getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise ValueError("Token does not contain email")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    access_token: str | None = Cookie(default=None), db=Depends(database.get_db)
):

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    email = verify_access_token(access_token)
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
