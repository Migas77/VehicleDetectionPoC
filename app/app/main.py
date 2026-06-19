from fastapi import FastAPI

from app.settings import settings

app = FastAPI(title=settings.poc_title)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
