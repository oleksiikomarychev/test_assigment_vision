import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from src.database import engine
from src.models import Base
from src.routers import image_router, websocket_router

load_dotenv()

def init_db():
    Base.metadata.create_all(bind=engine)

def dispose_db():
    engine.dispose()

def init_gemini():
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=gemini_api_key)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_gemini()
    yield
    dispose_db()


def create_app(router=None):
    app = FastAPI(
        title="Computer vision API",
        description="API for photo analysis",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(image_router, prefix="/image", tags=["image-related"])
    app.include_router(websocket_router, prefix="/ws", tags=["websocket-related"])

    return app