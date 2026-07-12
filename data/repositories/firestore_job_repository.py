import hashlib
import logging
from google.cloud import firestore
from domain.repositories.job_repository import JobRepository
from domain.entities.job import Job

logger = logging.getLogger("backend.data.repositories.firestore_job_repository")

class FirestoreJobRepository(JobRepository):
    def __init__(self, db: firestore.Client):
        self.db = db

    def calculate_sha256(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def check_and_filter_already_sent(self, jobs: list[Job]) -> list[Job]:
        filtered_jobs: list[Job] = []
        for job in jobs:
            url: str = job.url
            if not url:
                continue
            
            doc_id: str = self.calculate_sha256(url)
            
            try:
                doc_ref = self.db.collection("sent_jobs").document(doc_id)
                doc = doc_ref.get()
                if doc.exists:
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
            
            doc_id: str = self.calculate_sha256(url)
            try:
                doc_ref = self.db.collection("sent_jobs").document(doc_id)
                new_times_sent: int = job.times_sent + 1
                doc_ref.set({
                    "url": url,
                    "cargo": job.cargo,
                    "entidad": job.entidad,
                    "region": job.region,
                    "ciudad": job.ciudad,
                    "times_sent": new_times_sent,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                    "active": True
                }, merge=True)
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
