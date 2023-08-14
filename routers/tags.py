from fastapi import APIRouter

import sys
sys.path.append("..")

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    responses={404: {"description": "Not found"}}
)


@router.get("/")
async def first():
    return {"message": "Hello User, Choose Your Tag"}

