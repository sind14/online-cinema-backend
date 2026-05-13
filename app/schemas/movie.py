from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from app.schemas.certification import CertificationResponse
from app.schemas.genre import GenreResponse
from app.schemas.star import StarResponse
from app.schemas.director import DirectorResponse


class MovieBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None = None
    gross: float | None = None
    description: str
    price: Decimal


class MovieCreate(MovieBase):
    certification_id: int
    genre_ids: list[int] = Field(default_factory=list)
    star_ids: list[int] = Field(default_factory=list)
    director_ids: list[int] = Field(default_factory=list)


class MovieUpdate(BaseModel):
    name: str | None = None
    year: int | None = None
    time: int | None = None
    imdb: float | None = None
    votes: int | None = None
    meta_score: float | None = None
    gross: float | None = None
    description: str | None = None
    price: Decimal | None = None
    certification_id: int | None = None
    genre_ids: list[int] | None = None
    star_ids: list[int] | None = None
    director_ids: list[int] | None = None


class MovieResponse(MovieBase):
    id: int
    uuid: UUID
    certification_id: int

    model_config = {"from_attributes": True}


class MovieDetailResponse(MovieResponse):
    certification: CertificationResponse
    genres: list[GenreResponse] = Field(default_factory=list)
    stars: list[StarResponse] = Field(default_factory=list)
    directors: list[DirectorResponse] = Field(default_factory=list)
