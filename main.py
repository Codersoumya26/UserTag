from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def first():
    return {"message": "Hello User, Choose Your Tag"}
