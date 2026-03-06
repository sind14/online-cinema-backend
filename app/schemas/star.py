from app.schemas.base import NameBase, NameUpdate


class StarCreate(NameBase):
    pass


class StarUpdate(NameUpdate):
    pass


class StarResponse(NameBase):
    id: int

    model_config = {"from_attributes": True}
