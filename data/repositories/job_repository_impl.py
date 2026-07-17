import logging
import datetime
import json
import requests
from google.cloud import firestore
from domain.repositories.job_repository import JobRepository
from domain.entities.job import Job
from data.model.dto.sent_job_dto import SentJobDTO
from domain.exceptions.domain_exception import PortalConnectionError, DatabaseOperationError
from infrastructure.config import JOBS_PORTAL_URL, PORTAL_HEADERS

logger = logging.getLogger("backend.data.repositories.firestore_job_repository")

class JobRepositoryImpl(JobRepository):
    def __init__(self, db: firestore.Client):
        self.db = db

    def fetch_all_active_jobs(self) -> list[dict]:
        try:
            logger.info(f"Consultando ofertas vigentes en: {JOBS_PORTAL_URL}")
            response = requests.get(JOBS_PORTAL_URL, headers=PORTAL_HEADERS)

            if not response.ok:
                logger.error(f"HTTP error! status: {response.status_code}")
                raise PortalConnectionError(f"Error de red del portal. Status: {response.status_code}")
            
            text: str = response.text
            clean_text: str = text.replace("\ufeff", "").strip()
            parsed: dict = json.loads(clean_text)
            items: list[dict] = parsed.get("data", [])

            logger.info(f"Total de ofertas vigentes obtenidas del portal: {len(items)}")
            return items
        except Exception as e:
            if isinstance(e, PortalConnectionError):
                raise e
            logger.exception(f"Error al obtener las convocatorias desde el portal: {e}")
            raise PortalConnectionError(f"Error al obtener ofertas del portal: {e}")

    def get_sent_job_by_url(self, url: str) -> bool:
        try:
            docs = self.db.collection("sent_jobs").where(field_path="url", op_string="==", value=url).get()
            return len(docs) > 0
        except Exception as e:
            logger.error(f"Error consultando Firestore para {url}: {e}")
            raise DatabaseOperationError(f"Error consultando Firestore para {url}: {e}")

    def save_job(self, job: Job) -> None:
        try:
            dto = SentJobDTO(
                url=job.url,
                cargo=job.cargo,
                entidad=job.entidad,
                region=job.region,
                ciudad=job.ciudad,
                updated_at=None
            )
            data_to_save = dto.to_dict()
            data_to_save["updated_at"] = firestore.SERVER_TIMESTAMP
            self.db.collection("sent_jobs").document().set(data_to_save)
            logger.info(f"Se ha guardado la oferta nueva en Firestore: {job.url}")
        except Exception as e:
            logger.error(f"Error al guardar la oferta en Firestore para {job.url}: {e}")
            raise DatabaseOperationError(f"Error al guardar la oferta en Firestore para {job.url}: {e}")

    def fetch_all_sent_jobs(self) -> list[Job]:
        try:
            docs = self.db.collection("sent_jobs").stream()
            sent_jobs = []

            for doc in docs:
                data = doc.to_dict() or {}
                dto = SentJobDTO.from_dict(data)
                sent_jobs.append(
                    Job(
                        cargo=dto.cargo,
                        url=dto.url,
                        entidad=dto.entidad,
                        region=dto.region,
                        ciudad=dto.ciudad,
                        updated_at=dto.updated_at
                    )
                )
                
            return sent_jobs
        except Exception as e:
            logger.error(f"Error al obtener todas las ofertas enviadas: {e}")
            raise DatabaseOperationError(f"Error al obtener todas las ofertas enviadas: {e}")

    def delete_job_by_url(self, url: str) -> None:
        try:
            docs = self.db.collection("sent_jobs").where(field_path="url", op_string="==", value=url).get()
            for doc in docs:
                self.db.collection("sent_jobs").document(doc.id).delete()
            logger.info(f"Eliminado documento en Firestore para URL: {url}")
        except Exception as e:
            logger.error(f"Error al eliminar la oferta con URL {url}: {e}")
            raise DatabaseOperationError(f"Error al eliminar la oferta con URL {url}: {e}")