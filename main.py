import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from domain.exceptions.domain_exception import DomainException

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

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message
        }
    )

app.include_router(scripts_controller.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to your Cloud Run FastAPI Backend!",
        "status": "healthy"
    }
