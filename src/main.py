from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import engine
from src import models
from src.routers import router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router, prefix="/router", tags=["router"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)