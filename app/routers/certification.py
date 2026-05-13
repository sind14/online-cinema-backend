from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.certification import (
    CertificationCreate,
    CertificationUpdate,
    CertificationResponse,
)
from app.services.certification import CertificationService
from app.auth.dependencies import require_role
from app.models.user_groups import UserGroupEnum

router = APIRouter()
admin_router = APIRouter(dependencies=[Depends(require_role([UserGroupEnum.ADMIN]))])


@router.get("/", response_model=list[CertificationResponse])
def get_certifications(db: Session = Depends(get_db)):
    return CertificationService.get_all(db)


@admin_router.post(
    "/", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED
)
def create_certification(
    certification_in: CertificationCreate, db: Session = Depends(get_db)
):
    return CertificationService.create(db, **certification_in.model_dump())


@router.get("/{certification_id}", response_model=CertificationResponse)
def get_certification(certification_id: int, db: Session = Depends(get_db)):
    return CertificationService.get_or_404(db, certification_id)


@admin_router.put("/{certification_id}", response_model=CertificationResponse)
def update_certification(
    certification_id: int,
    certification_in: CertificationUpdate,
    db: Session = Depends(get_db),
):
    certification = CertificationService.get_or_404(db, certification_id)
    return CertificationService.update(
        db, certification, **certification_in.model_dump()
    )


@admin_router.delete("/{certification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(certification_id: int, db: Session = Depends(get_db)):
    certification = CertificationService.get_or_404(db, certification_id)
    CertificationService.delete(db, certification)


router.include_router(admin_router)
