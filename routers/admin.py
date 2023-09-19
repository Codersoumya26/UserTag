from starlette import status
from starlette.responses import RedirectResponse
from fastapi import Depends, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from .auth import get_current_user, get_password_hash, CreateUser
import models
import sys
sys.path.append("..")

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="",
    tags=["admin"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/about", response_class=HTMLResponse)
async def get_about(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("about.html", {"request": request, "user": user})


@router.post("/add-admin")
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
