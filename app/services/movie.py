from math import ceil
from fastapi import HTTPException, status
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session, joinedload
from app.models.movies import Movie
from app.models.genres import Genre
from app.models.stars import Star
from app.models.directors import Director
from app.models.certifications import Certification


class MovieService:

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
    ):
        query = (
            db.query(Movie).options(
                joinedload(Movie.certification),
                joinedload(Movie.genres),
                joinedload(Movie.stars),
                joinedload(Movie.directors),
            )
        )

        if search:
            query = query.filter(Movie.name.ilike(f"%{search}%"))

        if year:
            query = query.filter(Movie.year == year)

        if imdb_min is not None:
            query = query.filter(Movie.imdb >= imdb_min)

        if imdb_max is not None:
            query = query.filter(Movie.imdb <= imdb_max)

        if price_min is not None:
            query = query.filter(Movie.price >= price_min)

        if price_max is not None:
            query = query.filter(Movie.price <= price_max)

        if genre_id:
            query = query.join(Movie.genres).filter(Genre.id == genre_id)

        if star_id:
            query = query.join(Movie.stars).filter(Star.id == star_id)

        if director_id:
            query = query.join(Movie.directors).filter(Director.id == director_id)

        allowed_sort_fields = {
            "id": Movie.id,
            "year": Movie.year,
            "imdb": Movie.imdb,
            "price": Movie.price,
            "votes": Movie.votes,
        }

        if sort_by not in allowed_sort_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}",
            )

        sort_column = allowed_sort_fields[sort_by]

        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        total = query.count()

        movies = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if total else 1,
            "items": movies,
        }

    @staticmethod
    def get_by_id(db: Session, movie_id: int):
        return (db.query(Movie).options(
            joinedload(Movie.certification),
            joinedload(Movie.genres),
            joinedload(Movie.stars),
            joinedload(Movie.directors),
        ).filter(Movie.id == movie_id).first())

    @staticmethod
    def get_or_404(db, movie_id: int):
        movie = MovieService.get_by_id(db, movie_id)
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie with id {movie_id} not found",
            )
        return movie

    @staticmethod
    def create(db: Session, data):
        certification = db.query(Certification).filter(Certification.id == data.certification_id).first()
        if not certification:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid certification id")

        genres = db.query(Genre).filter(Genre.id.in_(data.genre_ids)).all()
        if len(genres) != len(data.genre_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more genre_ids are invalid")

        stars = db.query(Star).filter(Star.id.in_(data.star_ids)).all()
        if len(stars) != len(data.star_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more star_ids are invalid")

        directors = db.query(Director).filter(Director.id.in_(data.director_ids)).all()
        if len(directors) != len(data.director_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more director_ids are invalid")

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
    def update(db: Session, movie: Movie, data):
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in [
                "genres_ids",
                "stars_ids",
                "directors_ids",
            ]:
                continue
            setattr(movie, field, value)

        if data.genre_ids is not None:
            genres = db.query(Genre).filter(Genre.id.in_(data.genre_ids)).all()
            if len(genres) != len(data.genre_ids):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid genre_ids")
            movie.genres = genres

        if data.star_ids is not None:
            stars = db.query(Star).filter(Star.id.in_(data.star_ids)).all()
            if len(stars) != len(data.star_ids):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid star_ids")
            movie.stars = stars

        if data.director_ids is not None:
            directors = db.query(Director).filter(Director.id.in_(data.director_ids)).all()
            if len(directors) != len(data.director_ids):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid director_ids")
            movie.directors = directors

        db.commit()
        db.refresh(movie)

        return movie

    @staticmethod
    def delete(db: Session, movie: Movie):
        db.delete(movie)
        db.commit()
