from app.models.stars import Star
from app.services.base import BaseCRUDService


class StarService(BaseCRUDService):
    model = Star
    unique_field = "name"
