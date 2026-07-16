import logging
from fastapi import APIRouter, Depends

from domain.usecases.run_kine_job_finder_usecase import RunKineJobFinderUseCase
from domain.usecases.run_matron_job_finder_usecase import RunMatronJobFinderUseCase
from domain.usecases.cleanup_inactive_jobs_usecase import CleanupInactiveJobsUseCase
from infrastructure.dependencies import (
    get_run_kine_job_finder_usecase,
    get_run_matron_job_finder_usecase,
    get_cleanup_inactive_jobs_usecase
)
from infrastructure.middleware import verify_security_from_google_cloud_scheduler_task

logger = logging.getLogger("backend.controllers.scripts")

router = APIRouter(
    prefix="/scripts",
    tags=["scripts"]
)

@router.get("/run-job-finder/kinesiologia", dependencies=[Depends(verify_security_from_google_cloud_scheduler_task)])
async def run_kine_job_finder(
    usecase: RunKineJobFinderUseCase = Depends(get_run_kine_job_finder_usecase)
):
    usecase.execute()
    return {"status": "success", "message": "Búsqueda y notificación de ofertas para Kinesiología finalizada con éxito."}

@router.get("/run-job-finder/matroneria", dependencies=[Depends(verify_security_from_google_cloud_scheduler_task)])
async def run_matron_job_finder(
    usecase: RunMatronJobFinderUseCase = Depends(get_run_matron_job_finder_usecase)
):
    usecase.execute()
    return {"status": "success", "message": "Búsqueda y notificación de ofertas para Matronería finalizada con éxito."}

@router.get("/run-job-finder/cleanup", dependencies=[Depends(verify_security_from_google_cloud_scheduler_task)])
async def cleanup_inactive_jobs(
    usecase: CleanupInactiveJobsUseCase = Depends(get_cleanup_inactive_jobs_usecase)
):
    usecase.execute()
    return {"status": "success", "message": "Limpieza de ofertas cerradas en Firestore finalizada con éxito."}
