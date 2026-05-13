from pydantic import BaseModel, Field


class NameBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class NameUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
