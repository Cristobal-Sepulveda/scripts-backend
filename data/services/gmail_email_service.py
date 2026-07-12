import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from domain.services.email_service import EmailService

logger = logging.getLogger("backend.data.services.gmail_email_service")

class GmailEmailService(EmailService):
    def __init__(self, email_user: str = None, email_pass: str = None):
        self.email_user = email_user or os.environ.get("EMAIL_USER")
        self.email_pass = email_pass or os.environ.get("EMAIL_PASS")
        if not self.email_user or not self.email_pass:
            raise ValueError("Error: EMAIL_USER o EMAIL_PASS no configurados en las variables de entorno.")
        self.server = None

    def __enter__(self):
        try:
            self.server = smtplib.SMTP("smtp.gmail.com", 587)
            self.server.starttls()
            self.server.login(self.email_user, self.email_pass)
            return self
        except Exception as e:
            logger.exception("Error al conectar al servidor SMTP de Gmail")
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            try:
                self.server.quit()
            except Exception as e:
                logger.error(f"Error cerrando conexion SMTP: {e}")
            finally:
                self.server = None

    def send_email(self, recipients: list[str], subject: str, body: str) -> bool:
        if not self.server:
            logger.error("No hay conexion SMTP activa para enviar el correo.")
            return False

        msg = MIMEMultipart()
        msg["From"] = self.email_user
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        try:
            self.server.sendmail(self.email_user, recipients, msg.as_string())
            logger.info(f"Correo enviado exitosamente a {', '.join(recipients)}")
            return True
        except Exception as e:
            logger.error(f"Error al enviar correo a {', '.join(recipients)}: {e}")
            return False

    def get_sender_email(self) -> str:
        return self.email_user
