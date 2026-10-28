from fastapi import FastAPI
from sqlalchemy import text

from app.database import Base, engine
from app import models
from app.routers.questions import router as questions_router
from app.routers.reviews import router as reviews_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Q-Forge AI API",
    description="AI-powered question bank generation and review backend.",
    version="1.0.0",
)

app.include_router(questions_router)
app.include_router(reviews_router)


@app.get("/")
def home():
    return {"message": "Q-Forge AI backend is running!", "docs": "/docs"}


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}
