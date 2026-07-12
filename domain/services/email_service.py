from abc import ABC, abstractmethod

class EmailService(ABC):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def send_email(self, recipients: list[str], subject: str, body: str) -> bool:
        pass

    @abstractmethod
    def get_sender_email(self) -> str:
        pass
