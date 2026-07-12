import time
import logging
from fastapi import FastAPI, Request, HTTPException

logger = logging.getLogger("backend.middleware")

def register_logging_middleware(app: FastAPI):
    @app.middleware("http")
    async def log_and_time_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        
        client_host = request.client.host if request.client else "unknown"
        
        logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Client: {client_host} | "
            f"Time: {process_time:.4f}s"
        )
        return response

async def verify_security_from_google_cloud_scheduler_task(request: Request):
    client_host = request.client.host if request.client else "unknown"
    is_local = client_host in ("127.0.0.1", "localhost", "testclient")
    is_cloud_scheduler = (
        request.headers.get("X-CloudScheduler") == "true" or
        "Google-Cloud-Scheduler" in request.headers.get("user-agent", "")
    )
    
    if not (is_local or is_cloud_scheduler):
        logger.warning(f"Unauthorized access attempt to administrative endpoint from: {client_host}")
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Access denied. This endpoint is restricted to Cloud Scheduler or local requests."
        )
