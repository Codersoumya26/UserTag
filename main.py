from fastapi import FastAPI
import models
from database import engine
from routers import tags, auth
from starlette.staticfiles import StaticFiles


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(tags.router)
app.include_router(auth.router)
