from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.star import StarCreate, StarUpdate, StarResponse
from app.services.star import StarService
from app.auth.dependencies import require_role
from app.models.user_groups import UserGroupEnum

router = APIRouter()
admin_router = APIRouter(dependencies=[Depends(require_role([UserGroupEnum.ADMIN]))])


@router.get("/", response_model=list[StarResponse])
def get_stars(db: Session = Depends(get_db)):
    return StarService.get_all(db)


@admin_router.post(
    "/", response_model=StarResponse, status_code=status.HTTP_201_CREATED
)
def create_star(star_in: StarCreate, db: Session = Depends(get_db)):
    return StarService.create(db, **star_in.model_dump())


@router.get("/{star_id}", response_model=StarResponse)
def get_star(star_id: int, db: Session = Depends(get_db)):
    return StarService.get_or_404(db, star_id)


@admin_router.put("/{star_id}", response_model=StarResponse)
def update_star(star_id: int, star_in: StarUpdate, db: Session = Depends(get_db)):
    star = StarService.get_or_404(db, star_id)
    return StarService.update(db, star, **star_in.model_dump())


@admin_router.delete("/{star_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_star(star_id: int, db: Session = Depends(get_db)):
    star = StarService.get_or_404(db, star_id)
    StarService.delete(db, star)


router.include_router(admin_router)
