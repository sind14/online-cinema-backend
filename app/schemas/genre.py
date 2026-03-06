from app.schemas.base import NameBase, NameUpdate


class GenreCreate(NameBase):
    pass


class GenreUpdate(NameUpdate):
    pass


class GenreResponse(NameBase):
    id: int

    model_config = {"from_attributes": True}
