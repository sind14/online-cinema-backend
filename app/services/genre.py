from app.models.genres import Genre
from app.services.base import BaseCRUDService

class GenreService(BaseCRUDService):
    model = Genre
    unique_field = "name"
