from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "estudiante"
    COMPANY = "empresa"

class JobType(str, Enum):
    PRACTICA = "practica"
    PASANTIA = "pasantia"
    JUNIOR = "junior"
    MEDIO = "medio"
    SENIOR = "senior"

class JobModality(str, Enum):
    REMOTO = "remoto"
    PRESENCIAL = "presencial"
    HIBRIDO = "hibrido"

class ApplicationStatus(str, Enum):
    NUEVO = "nuevo"
    EN_REVISION = "en_revision"
    ENTREVISTA = "entrevista"
    OFERTA = "oferta"
    RECHAZADO = "rechazado"

class ApplyType(str, Enum):
    INTERNO = "interno"
    EXTERNO = "externo"