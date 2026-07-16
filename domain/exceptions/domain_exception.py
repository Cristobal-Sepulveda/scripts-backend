class DomainException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class PortalConnectionError(DomainException):
    def __init__(self, message: str = "Error al conectar con el portal externo de ofertas"):
        super().__init__(message=message, status_code=503)

class DatabaseOperationError(DomainException):
    def __init__(self, message: str = "Error al realizar operaciones en la base de datos"):
        super().__init__(message=message, status_code=500)

class EmailDispatchError(DomainException):
    def __init__(self, message: str = "Error al despachar las notificaciones de correo"):
        super().__init__(message=message, status_code=500)
