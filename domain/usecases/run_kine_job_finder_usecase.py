import re
from infrastructure import config
from domain.repositories.job_repository import JobRepository
from domain.services.email_service import EmailService
from domain.entities.job import Job
from domain.exceptions.domain_exception import EmailDispatchError

class RunKineJobFinderUseCase:
    def __init__(self, job_repository: JobRepository, email_service: EmailService):
        self.job_repository = job_repository
        self.email_service = email_service

    def execute(self) -> list[Job]:
        all_items = self.job_repository.fetch_all_active_jobs()
        if not all_items:
            return []
        kine_jobs_raw = self.filter_jobs(items=all_items, pattern=config.KINE_PATTERN)
        kine_jobs: list[Job] = []
        for job in kine_jobs_raw:
            persisted = self.job_repository.get_sent_job_by_url(job.url)
            if persisted:
                if persisted.times_sent >= 2:
                    continue
                job.times_sent = persisted.times_sent
            else:
                job.times_sent = 0
            kine_jobs.append(job)

        sender_email = self.email_service.get_sender_email()
        kine_mail_list = list(set(config.KINE_RECIPIENTS + [sender_email]))

        if len(kine_jobs) > 0:
            links_text = "".join(f"   {idx + 1}) {job.url} ({job.ciudad}, {job.entidad})\n" for idx, job in enumerate(kine_jobs))
            kine_body = f"hola hermano, te comparto oportunidades de trabajo en tu carrera en la Provincia de Santiago:\n\n{links_text}\npostule, buena suerte, saludos"
            kine_subject = "Oportunidades de trabajo para Kinesiólogo (Santiago)"
            kine_sent_ok = self.email_service.send_email(recipients=kine_mail_list, subject=kine_subject, body=kine_body)
            if not kine_sent_ok:
                raise EmailDispatchError("No se pudo enviar el correo de ofertas de Kinesiología")
            self.job_repository.increment_sent_count(kine_jobs)

        return kine_jobs

    def filter_jobs(self, items: list[dict], pattern: re.Pattern) -> list[Job]:
        jobs: list[Job] = []
        for item in items:
            cargo: str = item.get("Cargo") or ""
            entidad: str = item.get("Institución / Entidad") or ""
            region: str = item.get("Región") or ""
            ciudad: str = item.get("Ciudad") or ""

            if pattern.search(cargo) and self.is_in_santiago_province(region=region, city=ciudad):
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
            city_lower in config.SANTIAGO_PROVINCE_COMMUNES or
            strip_accents(city_lower) in config.SANTIAGO_PROVINCE_COMMUNES
        )
