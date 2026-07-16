from infrastructure import config
from domain.repositories.job_repository import JobRepository
from domain.services.email_service import EmailService

class RunJobFinderUseCase:
    def __init__(
        self,
        job_repository: JobRepository,
        email_service: EmailService
    ):
        self.job_repository = job_repository
        self.email_service = email_service

    def execute(self) -> None:
        all_items = self.job_repository.fetch_all_active_jobs()
        
        if not all_items:
            return

        kine_jobs_raw = self.filter_jobs(all_items, config.KINE_PATTERN)
        kine_jobs = self.job_repository.check_and_filter_already_sent(kine_jobs_raw)

        matron_jobs_raw = self.job_repository.filter_jobs(all_items, config.MATRON_PATTERN)
        matron_jobs = self.job_repository.check_and_filter_already_sent(matron_jobs_raw)

        sender_email = self.email_service.get_sender_email()
        
        kine_mail_list = list(set(config.KINE_RECIPIENTS + [sender_email]))
        if len(kine_jobs) > 0:
            links_text = "".join(f"   {idx + 1}) {job.url} ({job.ciudad}, {job.entidad})\n" for idx, job in enumerate(kine_jobs))
            kine_body = f"hola hermano, te comparto oportunidades de trabajo en tu carrera en la Provincia de Santiago:\n\n{links_text}\npostule, buena suerte, saludos"
            kine_subject = "Oportunidades de trabajo para Kinesiólogo (Santiago)"
            kine_sent_ok = self.email_service.send_email(kine_mail_list, kine_subject, kine_body)
            if kine_sent_ok:
                self.job_repository.increment_sent_count(kine_jobs)

        matron_mail_list = list(set(config.MATRON_RECIPIENTS + [sender_email]))
        if len(matron_jobs) > 0:
            links_text = "".join(f"   {idx + 1}) {job.url} ({job.ciudad}, {job.entidad})\n" for idx, job in enumerate(matron_jobs))
            matron_body = f"Hola María José, espero que estés muy bien.\n\nTe comparto las oportunidades de trabajo de matrón(a) en la Provincia de Santiago que encontré vigentes en el portal de Empleos Públicos:\n\n{links_text}\nEspero que te sirva alguno. ¡Mucho éxito en la búsqueda!\n\nSaludos"
            matron_subject = "Oportunidades de trabajo para Matrón(a) (Santiago)"
            matron_sent_ok = self.email_service.send_email(matron_mail_list, matron_subject, matron_body)
            if matron_sent_ok:
                self.job_repository.increment_sent_count(matron_jobs)

        active_urls = {
            item.get("url") or item.get("URL")
            for item in all_items
            if item.get("url") or item.get("URL")
        }
        
        self.job_repository.cleanup_inactive_jobs(active_urls)

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