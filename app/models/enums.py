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
    APPLIED = "applied"  # Recién postulado
    IN_REVIEW = "in_review"  # En revisión
    INTERVIEW = "interview"  # Entrevista programada
    OFFER = "offer"  # Oferta realizada
    ACCEPTED = "accepted"  # Aceptado
    REJECTED = "rejected"  # Rechazado
    WITHDRAWN = "withdrawn"  # Retirado por el candidato

class SavedItemType(str, Enum):
    JOB = "job"
    COURSE = "course"
    EVENT = "event"
    COMPANY = "company"

class EventRegistrationStatus(str, Enum):
    REGISTERED = "registered"
    ATTENDED = "attended"
    CANCELLED = "cancelled"

class ScholarshipStatus(str, Enum):
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class ApplyType(str, Enum):
    INTERNO = "interno"
    EXTERNO = "externo"