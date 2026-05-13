from math import ceil
from fastapi import HTTPException, status
from sqlalchemy import desc, asc, select
from sqlalchemy.orm import Session, joinedload
from app.models.movies import Movie
from app.models.genres import Genre
from app.models.stars import Star
from app.models.directors import Director
from app.models.certifications import Certification
from app.services.base import BaseCRUDService


class MovieService(BaseCRUDService):
    model = Movie

    @staticmethod
    def _get_entities_or_404(db: Session, model, ids: list[int], field_name: str):
        stmt = select(model).where(model.id.in_(ids))
        entities = db.scalars(stmt).all()

        if len(entities) != len(ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"One or more {field_name} are invalid",
            )

        return entities

    @staticmethod
    def get_all(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "id",
        order: str = "asc",
        search: str | None = None,
        year: int | None = None,
        imdb_min: float | None = None,
        imdb_max: float | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        genre_id: int | None = None,
        star_id: int | None = None,
        director_id: int | None = None,
    ) -> dict:
        stmt = select(Movie).options(
            joinedload(Movie.genres),
            joinedload(Movie.stars),
            joinedload(Movie.directors),
            joinedload(Movie.certification),
        )

        if search:
            stmt = stmt.where(Movie.name.ilike(f"%{search}%"))

        if year:
            stmt = stmt.where(Movie.year == year)

        if imdb_min is not None:
            stmt = stmt.where(Movie.imdb >= imdb_min)

        if imdb_max is not None:
            stmt = stmt.where(Movie.imdb <= imdb_max)

        if price_min is not None:
            stmt = stmt.where(Movie.price >= price_min)

        if price_max is not None:
            stmt = stmt.where(Movie.price <= price_max)

        if genre_id:
            stmt = stmt.join(Movie.genres).where(Genre.id == genre_id)

        if star_id:
            stmt = stmt.join(Movie.stars).where(Star.id == star_id)

        if director_id:
            stmt = stmt.join(Movie.directors).where(Director.id == director_id)

        allowed_sort_fields = {
            "id": Movie.id,
            "year": Movie.year,
            "imdb": Movie.imdb,
            "price": Movie.price,
            "votes": Movie.votes,
        }

        if sort_by not in allowed_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort field: {sort_by}",
            )

        sort_column = allowed_sort_fields[sort_by]

        if order == "desc":
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(asc(sort_column))

        stmt = stmt.distinct()

        total = len(db.scalars(stmt).unique().all())

        movies = (
            db.scalars(stmt.offset((page - 1) * page_size).limit(page_size))
            .unique()
            .all()
        )

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if total else 1,
            "items": movies,
        }

    @staticmethod
    def create_movie(db: Session, data) -> Movie:

        certification = db.get(Certification, data.certification_id)
        if not certification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid certification id",
            )

        genres = MovieService._get_entities_or_404(
            db, Genre, data.genre_ids, "genre_ids"
        )
        stars = MovieService._get_entities_or_404(db, Star, data.star_ids, "star_ids")
        directors = MovieService._get_entities_or_404(
            db, Director, data.director_ids, "director_ids"
        )

        movie = Movie(
            name=data.name,
            year=data.year,
            time=data.time,
            imdb=data.imdb,
            votes=data.votes,
            meta_score=data.meta_score,
            gross=data.gross,
            description=data.description,
            price=data.price,
            certification_id=data.certification_id,
        )

        movie.genres = genres
        movie.stars = stars
        movie.directors = directors

        db.add(movie)
        db.commit()
        db.refresh(movie)

        return movie

    @staticmethod
    def update_movie(db: Session, movie: Movie, data) -> Movie:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ["genre_ids", "star_ids", "director_ids"]:
                continue
            setattr(movie, field, value)

        if data.genre_ids is not None:
            movie.genres = MovieService._get_entities_or_404(
                db, Genre, data.genre_ids, "genre_ids"
            )

        if data.star_ids is not None:
            movie.stars = MovieService._get_entities_or_404(
                db, Star, data.star_ids, "star_ids"
            )

        if data.director_ids is not None:
            movie.directors = MovieService._get_entities_or_404(
                db, Director, data.director_ids, "director_ids"
            )

        db.commit()
        db.refresh(movie)

        return movie
