from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import Base, engine
from app.routers import notes


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Knowledge Base",
    description="Заметки с поиском по смыслу (TF-IDF) и обнаружением дублей.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(notes.router)


@app.get("/health")
def health():
    return {"status": "ok"}
