"""Pydantic response schemas."""
from pydantic import BaseModel, ConfigDict


class MovieOut(BaseModel):
    id: int
    tmdb_id: int | None = None
    title: str
    overview: str = ""
    poster_path: str | None = None
    backdrop_path: str | None = None
    release_date: str | None = None
    vote_average: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class SyncResult(BaseModel):
    imported: int
    message: str
