import logging
from fastapi import APIRouter, Depends, HTTPException

from domain.usecases.run_job_finder_usecase import RunJobFinderUseCase
from infrastructure.dependencies import get_run_job_finder_usecase
from infrastructure.middleware import verify_security_from_google_cloud_scheduler_task

logger = logging.getLogger("backend.controllers.scripts")

router = APIRouter(
    prefix="/scripts",
    tags=["scripts"]
)

@router.get("/run-job-finder", dependencies=[Depends(verify_security_from_google_cloud_scheduler_task)])
async def run_job_finder(runJobFinderUseCase: RunJobFinderUseCase = Depends(get_run_job_finder_usecase)):
    try:
        runJobFinderUseCase.execute()
    except ValueError as ve:
        error_msg = str(ve)
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Error interno en la ejecución del flujo: {e}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    return {"status": "success", "message": "Proceso de búsqueda de empleo finalizado con éxito."}
