from app.schemas.base import NameBase, NameUpdate


class CertificationCreate(NameBase):
    pass


class CertificationUpdate(NameUpdate):
    pass


class CertificationResponse(NameBase):
    id: int

    model_config = {"from_attributes": True}
