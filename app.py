
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import Base, engine
from models.product_model import Product
from routes.product_routes import router as product_router


IMG_DIR = Path(__file__).resolve().parent / "img"
IMG_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="E-commerce Backend",
    lifespan=lifespan
)


app.mount("/img", StaticFiles(directory=str(IMG_DIR)), name="img")

app.include_router(product_router)


@app.get("/")
def home():
    return {"message": "E-commerce Backend API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
