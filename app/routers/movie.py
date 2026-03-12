from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.movie import MovieResponse, MovieCreate, MovieUpdate, MovieDetailResponse
from app.services.movie import MovieService
from app.schemas.pagination import PaginationResponse
from app.auth.dependencies import require_role
from app.models.user_groups import UserGroupEnum

router = APIRouter()
admin_router = APIRouter(dependencies=[Depends(require_role([UserGroupEnum.ADMIN]))])


@router.get("/", response_model=PaginationResponse[MovieResponse])
def get_movies(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        sort_by: str = Query("id"),
        order: str = Query("asc", pattern="^(asc|desc)$"),
        search: str | None = None,
        year: int | None = None,
        imdb_min: float | None = None,
        imdb_max: float | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        genre_id: int | None = None,
        star_id: int | None = None,
        director_id: int | None = None,
        db: Session = Depends(get_db),
):
    return MovieService.get_all(
        db,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        search=search,
        year=year,
        imdb_min=imdb_min,
        imdb_max=imdb_max,
        price_min=price_min,
        price_max=price_max,
        genre_id=genre_id,
        star_id=star_id,
        director_id=director_id,
    )


@admin_router.post("/", response_model=MovieResponse)
def create_movie(movie_in: MovieCreate, db: Session = Depends(get_db)):
    return MovieService.create_movie(db, movie_in)


@router.get("/{movie_id}", response_model=MovieDetailResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    return MovieService.get_or_404(db, movie_id)


@admin_router.put("/{movie_id}", response_model=MovieResponse)
def update_movie(movie_id: int, movie_in: MovieUpdate, db: Session = Depends(get_db)):
    movie = MovieService.get_or_404(db, movie_id)
    return MovieService.update_movie(db, movie, movie_in)


@admin_router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = MovieService.get_or_404(db, movie_id)
    MovieService.delete(db, movie)


router.include_router(admin_router)
