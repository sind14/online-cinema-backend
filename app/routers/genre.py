from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.genre import GenreCreate, GenreUpdate, GenreResponse
from app.services.genre import GenreService
from app.auth.dependencies import require_role
from app.models.user_groups import UserGroupEnum

router = APIRouter()
admin_router = APIRouter(dependencies=[Depends(require_role([UserGroupEnum.ADMIN]))])


@router.get("/", response_model=list[GenreResponse])
def get_genres(db: Session = Depends(get_db)):
    return GenreService.get_all(db)


@admin_router.post(
    "/", response_model=GenreResponse, status_code=status.HTTP_201_CREATED
)
def create_genre(genre_in: GenreCreate, db: Session = Depends(get_db)):
    return GenreService.create(db, **genre_in.model_dump())


@router.get("/{genre_id}", response_model=GenreResponse)
def get_genre(genre_id: int, db: Session = Depends(get_db)):
    return GenreService.get_or_404(db, genre_id)


@admin_router.put("/{genre_id}", response_model=GenreResponse)
def update_genre(genre_id: int, genre_in: GenreUpdate, db: Session = Depends(get_db)):
    genre = GenreService.get_or_404(db, genre_id)
    return GenreService.update(db, genre, **genre_in.model_dump())


@admin_router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = GenreService.get_or_404(db, genre_id)
    GenreService.delete(db, genre)


router.include_router(admin_router)
