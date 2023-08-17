from starlette import status
from starlette.responses import RedirectResponse
from typing import Optional
from fastapi import Depends, APIRouter, HTTPException, Request
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
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


class Tag(BaseModel):
    name: str
    description: Optional[str]
    # ratings: int = Field(gt=0, lt=6, description="The ratings must be between 1-5")
    popular: bool


@router.get("/", response_class=HTMLResponse)
# async def get_all_tag_by_user(request: Request, db: Session = Depends(get_db)):
async def get_all_tag(request: Request, db: Session = Depends(get_db)):
    tags = db.query(models.Tags).all()
    return templates.TemplateResponse("home.html", {"request": request, "tags": tags})


@router.get("/{tag_id}")
async def get_tag_by_id(tag_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Tags)\
        .filter(models.Tags.id == tag_id)\
        .first()
    if todo_model is not None:
        return todo_model
    raise http_exception()


@router.post("/add-tag")
async def add_tag(tag: Tag, db: Session = Depends(get_db)):
    tag_model = models.Tags()
    tag_model.name = tag.name
    tag_model.description = tag.description
    tag_model.popular = tag.popular
    # tag_model.owner_id = 1

    db.add(tag_model)
    db.commit()

    return successful_response(201)


def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }


def http_exception():
    return HTTPException(status_code=404, detail="Tag not found")


# @router.get("/add-tag", response_class=HTMLResponse)
# async def add_new_tag(request: Request):
#
#     return templates.TemplateResponse("add-tag.html", {"request": request})
