from app.models.certifications import Certification
from app.services.base import  BaseCRUDService

class CertificationService(BaseCRUDService):
    model = Certification
    unique_field = "name"
