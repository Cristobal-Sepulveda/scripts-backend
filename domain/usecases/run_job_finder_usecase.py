from infrastructure import config
from domain.repositories.job_repository import JobRepository
from domain.services.email_service import EmailService
from domain.repositories.job_datasource import JobDataSource

class RunJobFinderUseCase:
    def __init__(
        self,
        job_repository: JobRepository,
        email_service: EmailService,
        portal_client: JobDataSource
    ):
        self.job_repository = job_repository
        self.email_service = email_service
        self.portal_client = portal_client

    def execute(self) -> None:
        all_items = self.portal_client.fetch_all_active_jobs()
        if not all_items:
            return

        kine_jobs_raw = self.portal_client.filter_jobs(all_items, config.KINE_PATTERN)
        kine_jobs = self.job_repository.check_and_filter_already_sent(kine_jobs_raw)

        matron_jobs_raw = self.portal_client.filter_jobs(all_items, config.MATRON_PATTERN)
        matron_jobs = self.job_repository.check_and_filter_already_sent(matron_jobs_raw)

        with self.email_service as service:
            sender_email = service.get_sender_email()
            
            kine_mail_list = list(set(config.KINE_RECIPIENTS + [sender_email]))
            if len(kine_jobs) > 0:
                links_text = "".join(f"   {idx + 1}) {job.url} ({job.ciudad}, {job.entidad})\n" for idx, job in enumerate(kine_jobs))
                kine_body = f"hola hermano, te comparto oportunidades de trabajo en tu carrera en la Provincia de Santiago:\n\n{links_text}\npostule, buena suerte, saludos"
                kine_subject = "Oportunidades de trabajo para Kinesiólogo (Santiago)"
                kine_sent_ok = service.send_email(kine_mail_list, kine_subject, kine_body)
                if kine_sent_ok:
                    self.job_repository.increment_sent_count(kine_jobs)

            matron_mail_list = list(set(config.MATRON_RECIPIENTS + [sender_email]))
            if len(matron_jobs) > 0:
                links_text = "".join(f"   {idx + 1}) {job.url} ({job.ciudad}, {job.entidad})\n" for idx, job in enumerate(matron_jobs))
                matron_body = f"Hola María José, espero que estés muy bien.\n\nTe comparto las oportunidades de trabajo de matrón(a) en la Provincia de Santiago que encontré vigentes en el portal de Empleos Públicos:\n\n{links_text}\nEspero que te sirva alguno. ¡Mucho éxito en la búsqueda!\n\nSaludos"
                matron_subject = "Oportunidades de trabajo para Matrón(a) (Santiago)"
                matron_sent_ok = service.send_email(matron_mail_list, matron_subject, matron_body)
                if matron_sent_ok:
                    self.job_repository.increment_sent_count(matron_jobs)

            active_urls = {
                item.get("url") or item.get("URL")
                for item in all_items
                if item.get("url") or item.get("URL")
            }
            
            self.job_repository.cleanup_inactive_jobs(active_urls)
