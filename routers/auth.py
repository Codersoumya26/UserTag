from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import sys
import models
from database import SessionLocal, engine

sys.path.append("..")


class CreateUser(BaseModel):
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return bcrypt_context.hash(password)


@router.post("/create/user")
async def create_new_user(new_user: CreateUser, db: Session = Depends(get_db)):
    new_user_model = models.Users()
    new_user_model.email = new_user.email
    new_user_model.username = new_user.username
    new_user_model.first_name = new_user.first_name
    new_user_model.last_name = new_user.last_name
    new_user_model.is_active = True

    hash_password = get_password_hash(new_user.password)
    new_user_model.hashed_password = hash_password

    db.add(new_user_model)
    db.commit()


@router.get("/", response_class=HTMLResponse)
async def get_authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception
