import logging
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from controllers import scripts_controller
from infrastructure.middleware import register_logging_middleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

app = FastAPI(
    title="GCLOUD RUN FastAPI Backend",
    description="Backend para tareas programadas de administración y endpoints exploratorios",
    version="1.0.0"
)

register_logging_middleware(app)

app.include_router(scripts_controller.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to your Cloud Run FastAPI Backend!",
        "status": "healthy"
    }
