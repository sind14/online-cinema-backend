from pydantic import BaseModel
from app.schemas.movie import MovieResponse


class CartItemResponse(BaseModel):
    id: int
    movie: MovieResponse

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]

    model_config = {"from_attributes": True}


class CartItemCreate(BaseModel):
    movie_id: int
