import re
import logging
from infrastructure import config
from domain.repositories.job_repository import JobRepository
from domain.services.email_service import EmailService
from domain.entities.job import Job
from domain.exceptions.domain_exception import EmailDispatchError

logger = logging.getLogger("backend.domain.usecases.run_kine_job_finder")

class RunKineJobFinderUseCase:
    def __init__(self, job_repository: JobRepository, email_service: EmailService):
        self.job_repository = job_repository
        self.email_service = email_service

    def execute(self) -> None:
        logger.info("Iniciando búsqueda de ofertas laborales para Kinesiología...")
        newest_empleos_publicos_jobs = self.job_repository.fetch_all_active_jobs()

        if not newest_empleos_publicos_jobs:
            logger.info("No se encontraron ofertas activas en el portal público.")
            return

        logger.info(f"Se obtuvieron {len(newest_empleos_publicos_jobs)} ofertas activas del portal público.")

        parsed_kine_jobs_list = self._filter_jobs(
            jobs=newest_empleos_publicos_jobs, 
            pattern=config.KINE_PATTERN
        )

        if len(parsed_kine_jobs_list) == 0: 
            logger.info("No se encontraron ofertas que coinciden con Kinesiología en Santiago.")
            return None

        logger.info(f"Se encontraron {len(parsed_kine_jobs_list)} ofertas que coinciden con Kinesiología en Santiago.")
        
        kine_jobs: list[Job] = []

        for job in parsed_kine_jobs_list:
            if self.job_repository.get_sent_job_by_url(job.url): continue
            self.job_repository.save_job(job)
            kine_jobs.append(job)

        if len(kine_jobs) == 0:
            logger.info("No se encontraron ofertas nuevas de Kinesiología para enviar por correo.")
            return None

        sender_email = self.email_service.get_sender_email()
        kine_mail_list = list(set(config.KINE_RECIPIENTS + [sender_email]))

        logger.info(f"Se enviarán {len(kine_jobs)} nuevas ofertas por correo a: {kine_mail_list}")

        links_text = "".join(f"   {idx + 1}) {job.url} ({job.ciudad}, {job.entidad})\n" for idx, job in enumerate(kine_jobs))
        kine_body = f"hola hermano, te comparto oportunidades de trabajo en tu carrera en la Provincia de Santiago:\n\n{links_text}\npostule, buena suerte, saludos"
        kine_subject = "Oportunidades de trabajo para Kinesiólogo (Santiago)"
        kine_sent_ok = self.email_service.send_email(recipients=kine_mail_list, subject=kine_subject, body=kine_body)

        if not kine_sent_ok:
            logger.error("Error al enviar el correo SMTP con las ofertas.")
            raise EmailDispatchError("No se pudo enviar el correo de ofertas de Kinesiología")
        else:
            logger.info("Correo de ofertas enviado exitosamente.")

    def _filter_jobs(self, jobs: list[dict], pattern: re.Pattern) -> list[Job]:
        jobs_list: list[Job] = []

        for item in jobs:
            cargo: str = item.get("Cargo") or ""
            entidad: str = item.get("Institución / Entidad") or ""
            region: str = item.get("Región") or ""
            ciudad: str = item.get("Ciudad") or ""

            if pattern.search(cargo) and self._is_in_santiago_province(region=region, city=ciudad):
                job_url: str = item.get("url") or item.get("URL")
                if job_url:
                    jobs_list.append(Job(
                        cargo=cargo,
                        url=job_url,
                        entidad=entidad,
                        region=region,
                        ciudad=ciudad
                    ))

        return jobs_list

    def _is_in_santiago_province(self, region: str, city: str) -> bool:
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
            city_lower in config.SANTIAGO_PROVINCE_COMMUNES or
            strip_accents(city_lower) in config.SANTIAGO_PROVINCE_COMMUNES
        )
