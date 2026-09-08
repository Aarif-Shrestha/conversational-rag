from fastapi import FastAPI
from app.api.routes.documents import router as documents_router

app = FastAPI()

app.include_router(documents_router)


@app.get("/")
def root():
    return {
        "message": "It is running"
    }