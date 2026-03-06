from app.models.directors import Director
from app.services.base import  BaseCRUDService

class DirectorService(BaseCRUDService):
    model = Director
    unique_field = "name"
