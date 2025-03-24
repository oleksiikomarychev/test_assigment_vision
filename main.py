from fastapi import FastAPI

from src.database import engine
from src import models
from src.routers import router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router, prefix="/router", tags=["router"])