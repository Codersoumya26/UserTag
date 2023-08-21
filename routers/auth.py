from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal, engine
from datetime import datetime, timedelta
from jose import jwt, JWTError
import models
import sys

sys.path.append("..")


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


# Secret key to sign and verify tokens
SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

# Password hashing
bcrypt_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 PasswordBearer for token authentication
oauth2_bearer_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Function to verify access token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_password_hash(password):
    return bcrypt_pwd_context.hash(password)


# Function to verify user's password
def verify_password(plain_password, hashed_password):
    return bcrypt_pwd_context.verify(plain_password, hashed_password)


# Function to create access token
def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):
    to_encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to get current user based on token
async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = decode_token(token)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            return None
        return {"username": username, "id": user_id}
    except JWTError:
        raise get_user_exception()


# Function to authenticate user
def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users)\
        .filter(models.Users.username == username)\
        .first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Token endpoint to authenticate and generate token
@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=40)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


class CreateUser(BaseModel):
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    password: str


@router.post("/add/admin-user")
async def create_admin_user(new_user: CreateUser, db: Session = Depends(get_db)):
    new_user_model = models.Users()
    new_user_model.email = new_user.email
    new_user_model.username = new_user.username
    new_user_model.first_name = new_user.first_name
    new_user_model.last_name = new_user.last_name
    new_user_model.is_active = True
    new_user_model.is_admin = True

    hash_password = get_password_hash(new_user.password)
    new_user_model.hashed_password = hash_password

    db.add(new_user_model)
    db.commit()


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


@router.get("/", response_class=HTMLResponse)
async def get_authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/tags", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response


# Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception
