import re
import json
import logging
import requests
from infrastructure.config import JOBS_PORTAL_URL, PORTAL_HEADERS, SANTIAGO_PROVINCE_COMMUNES
from domain.entities.job import Job
from domain.repositories.job_datasource import JobDataSource

logger = logging.getLogger("backend.data.network.portal_client")

class PortalClient(JobDataSource):
    def is_in_santiago_province(self, region: str, city: str) -> bool:
        if not region or not city:
            return False
            
        region_lower = region.lower()
        city_lower = city.lower().strip()
        
        if "metropolitana" not in region_lower and "santiago" not in region_lower:
            return False
            
        def strip_accents(text: str) -> str:
            accents = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}
            for acc, rep in accents.items():
                text = text.replace(acc, rep)
            return text

        return (
            city_lower in SANTIAGO_PROVINCE_COMMUNES or 
            strip_accents(city_lower) in SANTIAGO_PROVINCE_COMMUNES
        )

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

    def filter_jobs(self, items: list[dict], pattern: re.Pattern) -> list[Job]:
        jobs: list[Job] = []
        for item in items:
            cargo: str = item.get("Cargo") or ""
            entidad: str = item.get("Institución / Entidad") or ""
            region: str = item.get("Región") or ""
            ciudad: str = item.get("Ciudad") or ""
            
            if pattern.search(cargo) and self.is_in_santiago_province(region, ciudad):
                job_url: str = item.get("url") or item.get("URL")
                if job_url:
                    jobs.append(Job(
                        cargo=cargo,
                        url=job_url,
                        entidad=entidad,
                        region=region,
                        ciudad=ciudad
                    ))
        return jobs
