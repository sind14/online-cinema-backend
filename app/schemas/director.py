from app.schemas.base import NameBase, NameUpdate


class DirectorCreate(NameBase):
    pass


class DirectorUpdate(NameUpdate):
    pass


class DirectorResponse(NameBase):
    id: int

    model_config = {"from_attributes": True}
