import logging
from google.cloud import firestore
from domain.repositories.job_repository import JobRepository
from domain.entities.job import Job

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
                return []
            
            text: str = response.text
            clean_text: str = text.replace("\ufeff", "").strip()
            parsed: dict = json.loads(clean_text)
            items: list[dict] = parsed.get("data", [])

            logger.info(f"Total de ofertas vigentes obtenidas del portal: {len(items)}")
            return items
        except Exception as e:
            logger.exception(f"Error al obtener las convocatorias desde el portal: {e}")
            return []

    def check_and_filter_already_sent(self, jobs: list[Job]) -> list[Job]:
        filtered_jobs: list[Job] = []
        for job in jobs:
            url: str = job.url
            if not url:
                continue
            
            try:
                docs = self.db.collection("sent_jobs").where(field_path="url", op_string="==", value=url).limit(1).get()
                if docs:
                    doc = docs[0]
                    data = doc.to_dict() or {}
                    times_sent: int = data.get("times_sent", 0)
                    if times_sent >= 2:
                        logger.info(f"Omitiendo oferta (ya enviada {times_sent} veces): {url}")
                        continue
                    job.times_sent = times_sent
                else:
                    job.times_sent = 0
                filtered_jobs.append(job)
            except Exception as e:
                logger.error(f"Error consultando Firestore para {url}: {e}. Se asume no enviado.")
                job.times_sent = 0
                filtered_jobs.append(job)
                
        return filtered_jobs

    def increment_sent_count(self, jobs: list[Job]) -> None:
        for job in jobs:
            url: str = job.url
            if not url:
                continue
            
            try:
                docs = self.db.collection("sent_jobs").where(field_path="url", op_string="==", value=url).limit(1).get()
                new_times_sent: int = job.times_sent + 1
                data_to_save = {
                    "url": url,
                    "cargo": job.cargo,
                    "entidad": job.entidad,
                    "region": job.region,
                    "ciudad": job.ciudad,
                    "times_sent": new_times_sent,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                    "active": True
                }
                if docs:
                    doc_ref = self.db.collection("sent_jobs").document(docs[0].id)
                    doc_ref.set(document_data=data_to_save, merge=True)
                else:
                    doc_ref = self.db.collection("sent_jobs").document()
                    doc_ref.set(data_to_save)
                logger.info(f"Incrementado contador de envíos para {url} a {new_times_sent}")
            except Exception as e:
                logger.error(f"Error actualizando contador en Firestore para {url}: {e}")

    def cleanup_inactive_jobs(self, active_urls: set[str]) -> None:
        try:
            docs = self.db.collection("sent_jobs").stream()
            for doc in docs:
                data = doc.to_dict() or {}
                url: str = data.get("url", "")
                if url and url not in active_urls:
                    logger.info(f"Eliminando oferta inactiva/cerrada de Firestore: {url}")
                    self.db.collection("sent_jobs").document(doc.id).delete()
        except Exception as e:
            logger.error(f"Error durante la limpieza de ofertas inactivas: {e}")
