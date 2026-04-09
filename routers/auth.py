from fastapi import APIRouter, Depends, HTTPException
import database
from schemas.user import User, UserCreate, UserLogin
from models.user import User as UserModel
from passlib.context import CryptContext
from utils.jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"])

router = APIRouter()


@router.post("/auth/register", status_code=201)
def register(user: UserCreate, db=Depends(database.get_db)):
    existing_user_email = (
        db.query(UserModel).filter(UserModel.email == user.email).first()
    )
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_user_username = (
        db.query(UserModel).filter(UserModel.username == user.username).first()
    )
    if existing_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = UserModel(
        username=user.username,
        email=user.email,
        password_hash=pwd_context.hash(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"User {user.username} registered successfully!"}


@router.post("/auth/login")
def login(user: UserLogin, db=Depends(database.get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
