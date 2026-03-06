from pydantic import BaseModel, Field
from typing import Optional, List
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
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: str
    price: float


class MovieCreate(MovieBase):
    certification_id: int
    genre_ids: List[int] = Field(default_factory=list)
    star_ids: List[int] = Field(default_factory=list)
    director_ids: List[int] = Field(default_factory=list)


class MovieUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    time: Optional[int] = None
    imdb: Optional[float] = None
    votes: Optional[int] = None
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: Optional[str] = None
    price: Optional[float] = None
    certification_id: Optional[int] = None
    genre_ids: Optional[List[int]] = None
    star_ids: Optional[List[int]] = None
    director_ids: Optional[List[int]] = None


class MovieResponse(MovieBase):
    id: int
    uuid: UUID
    certification_id: int

    model_config = {"from_attributes": True}


class MovieDetailResponse(MovieResponse):
    certification: CertificationResponse
    genres: List[GenreResponse] = Field(default_factory=list)
    stars: List[StarResponse] = Field(default_factory=list)
    directors: List[DirectorResponse] = Field(default_factory=list)
