import logging
from google.cloud import firestore
from domain.repositories.job_repository import JobRepository
from domain.entities.job import Job
from data.model.dto.sent_job_dto import SentJobDTO
from domain.exceptions.domain_exception import PortalConnectionError, DatabaseOperationError

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

    def get_sent_job_by_url(self, url: str) -> Job | None:
        try:
            docs = self.db.collection("sent_jobs").where(field_path="url", op_string="==", value=url).limit(count=1).get()
            if docs:
                doc = docs[0]
                doc_data = doc.to_dict() or {}
                dto = SentJobDTO.from_dict(doc_data)
                return Job(
                    cargo=dto.cargo,
                    url=dto.url,
                    entidad=dto.entidad,
                    region=dto.region,
                    ciudad=dto.ciudad,
                    times_sent=dto.times_sent,
                    active=dto.active
                )
            return None
        except Exception as e:
            logger.error(f"Error consultando Firestore para {url}: {e}")
            raise DatabaseOperationError(f"Error consultando Firestore para {url}: {e}")

    def increment_sent_count(self, jobs: list[Job]) -> None:
        for job in jobs:
            url: str = job.url
            if not url:
                continue
            
            try:
                docs = self.db.collection("sent_jobs").where(field_path="url", op_string="==", value=url).limit(1).get()
                new_times_sent: int = job.times_sent + 1
                dto = SentJobDTO(
                    url=url,
                    cargo=job.cargo,
                    entidad=job.entidad,
                    region=job.region,
                    ciudad=job.ciudad,
                    times_sent=new_times_sent,
                    active=True
                )
                data_to_save = dto.to_dict()
                data_to_save["updated_at"] = firestore.SERVER_TIMESTAMP
                if docs:
                    doc_ref = self.db.collection("sent_jobs").document(docs[0].id)
                    doc_ref.set(document_data=data_to_save, merge=True)
                else:
                    doc_ref = self.db.collection("sent_jobs").document()
                    doc_ref.set(data_to_save)
                logger.info(f"Incrementado contador de envíos para {url} a {new_times_sent}")
            except Exception as e:
                logger.error(f"Error actualizando contador en Firestore para {url}: {e}")
                raise DatabaseOperationError(f"Error actualizando contador en Firestore para {url}: {e}")

    def cleanup_inactive_jobs(self, active_urls: set[str]) -> None:
        try:
            docs = self.db.collection("sent_jobs").stream()
            for doc in docs:
                data = doc.to_dict() or {}
                dto = SentJobDTO.from_dict(data)
                url: str = dto.url
                if url and url not in active_urls:
                    logger.info(f"Eliminando oferta inactiva/cerrada de Firestore: {url}")
                    self.db.collection("sent_jobs").document(doc.id).delete()
        except Exception as e:
            logger.error(f"Error durante la limpieza de ofertas inactivas: {e}")
            raise DatabaseOperationError(f"Error durante la limpieza de ofertas inactivas: {e}")
