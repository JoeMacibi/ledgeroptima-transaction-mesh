import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import settings
from app.database import init_db, SessionLocal
from app.data_generator import seed_initial_data
from app.background_tasks import background_manager
from app.routes import transactions, merchants, system

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    db = SessionLocal()
    seed_initial_data(db, num_transactions=5000)
    db.close()
    
    background_manager.start()
    logger.info(f"Starting {settings.app_name}")
    yield
    background_manager.stop()
    logger.info("Shutting down")


app = FastAPI(
    title=settings.app_name,
    description="Enterprise transaction telemetry portal",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(transactions.router)
app.include_router(merchants.router)
app.include_router(system.router)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("templates/index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/health")
async def api_health():
    return {"status": "ok", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        workers=1 if settings.debug else 4,
    )
