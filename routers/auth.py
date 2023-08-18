from fastapi import APIRouter
import sys
sys.path.append("..")


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}}
)
