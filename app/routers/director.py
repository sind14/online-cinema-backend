from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.director import DirectorCreate, DirectorUpdate, DirectorResponse
from app.services.director import DirectorService
from app.auth.dependencies import require_role
from app.models.user_groups import UserGroupEnum


router = APIRouter()
admin_router = APIRouter(dependencies=[Depends(require_role([UserGroupEnum.ADMIN]))])


@router.get("/", response_model=list[DirectorResponse])
def get_directors(db: Session = Depends(get_db)):
    return DirectorService.get_all(db)


@admin_router.post("/", response_model=DirectorResponse, status_code=status.HTTP_201_CREATED)
def create_director(director_in: DirectorCreate, db: Session = Depends(get_db)):
    return DirectorService.create(db, **director_in.model_dump())


@router.get("/{director_id}", response_model=DirectorResponse)
def get_director(director_id: int, db: Session = Depends(get_db)):
    return DirectorService.get_or_404(db, director_id)


@admin_router.put("/{director_id}", response_model=DirectorResponse)
def update_director(director_id: int, director_in: DirectorUpdate, db: Session = Depends(get_db)):
    director = DirectorService.get_or_404(db, director_id)
    return DirectorService.update(db, director, **director_in.model_dump())


@admin_router.delete("/{director_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_director(director_id: int, db: Session = Depends(get_db)):
    director = DirectorService.get_or_404(db, director_id)
    DirectorService.delete(db, director)


router.include_router(admin_router)
