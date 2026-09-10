from fastapi import FastAPI
from app.api.routes.documents import router as documents_router
from app.core.database import Base, engine
from app.models.document import Document 
from app.api.routes.chat import router as chat_router
from app.models.booking import Booking  

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(documents_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {
        "message": "It is running"
    }