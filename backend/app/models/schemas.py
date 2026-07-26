from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserSignup(BaseModel):
    email: str
    password: str = Field(..., min_length=0)
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password:str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MovieResponse(BaseModel):
    id: int
    tmdb_id:int
    title: str
    overview: Optional[str]
    poster_path: Optional[str]
    release_date: Optional[str]
    runtime: Optional[int]
    genres: Optional[list]
    vote_average: Optional[float]

    class config:
        from_attributes = True

class WatchlistItemCreate(BaseModel):
    move_id: int
    status: str = "want_to_watch"

class WatchlistItemResponse(BaseModel):
    id:int
    movie_id:int
    status: str
    rating: Optional[int]
    movie: Optional[MovieResponse]
    added_at: Optional[datetime]

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str = Field(..., min_length = 1)
    session_id: Optional[int] = None

class ChatResponse(BaseModel):
    session_id: int
    message: str
    recommendations: list = []

