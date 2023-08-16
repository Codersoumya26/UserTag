from starlette import status
from starlette.responses import RedirectResponse
from typing import Optional
from fastapi import Depends, APIRouter, Request
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel

from fastapi.templating import Jinja2Templates

import sys
sys.path.append("..")

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    description: Optional[str]
    # ratings: int = Field(gt=0, lt=6, description="The ratings must be between 1-5")
    complete: bool


# @router.get("/test")
# async def test(request: Request):
#     return templates.TemplateResponse("add-tag.html", {"request": request})


@router.get("/")
async def get_all_tag(db: Session = Depends(get_db)):
    return db.query(models.Tags).all()

# @router.get("/", response_class=HTMLResponse)
# async def get_all_tag_by_user(request: Request, db: Session = Depends(get_db)):
#     tags = db.query(models.Tags).all()
#     return templates.TemplateResponse("home.html", {"request": request, "tags": tags})


# @router.get("/add-tag", response_class=HTMLResponse)
# async def add_new_tag(request: Request):
#
#     return templates.TemplateResponse("add-tag.html", {"request": request})
