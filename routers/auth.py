from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sys

sys.path.append("..")

templates = Jinja2Templates(directory="templates")
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_class=HTMLResponse)
async def get_authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
