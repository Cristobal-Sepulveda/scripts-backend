import datetime
import logging
from domain.repositories.job_repository import JobRepository

logger = logging.getLogger("backend.domain.usecases.cleanup_inactive_jobs")

class CleanupInactiveJobsUseCase:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def execute(self) -> None:
        logger.info("Iniciando proceso de limpieza de ofertas antiguas en Firestore...")
        
        sent_jobs = self.job_repository.fetch_all_sent_jobs()
        if not sent_jobs:
            logger.info("No se encontraron ofertas registradas en Firestore.")
            return

        threshold_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)
        logger.info(f"Fecha límite de antigüedad (1 mes): {threshold_date}")

        deleted_count = 0
        for job in sent_jobs:
            if job.updated_at and job.updated_at < threshold_date:
                logger.info(f"Eliminando oferta por antigüedad (más de 1 mes): {job.url} (Fecha: {job.updated_at})")
                self.job_repository.delete_job_by_url(job.url)
                deleted_count += 1

        logger.info(f"Proceso de limpieza finalizado con éxito. Se eliminaron {deleted_count} ofertas.")
