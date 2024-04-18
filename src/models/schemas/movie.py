import datetime
from typing import List, Optional

from pydantic import HttpUrl

from src.models.schemas.base import BaseSchemaModel




class ReviewBase(BaseSchemaModel):
    movie_id : int
    review : str
    rating : float

class ReviewInCreate(ReviewBase):
    pass

class ReviewInResponse(ReviewBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    account_id: int
    profile_picture: str
    username: str


class MovieBase(BaseSchemaModel):
    title: str
    description: str
    year: int
    rating: str
    genre: str
    director: str
    cast: str
    duration: int
    cover_image_url: HttpUrl

class MovieInCreate(MovieBase):
    pass




class AdminMovieInResponse(MovieBase):
    id: int
    is_verified: bool
    account_id: int

class RatingPercentages(BaseSchemaModel):
    average_rating: float
    rating_1: float
    rating_2: float
    rating_3: float
    rating_4: float
    rating_5: float

class MovieInResponse(MovieBase):
    id: int
    reviews: Optional[List[ReviewInResponse]] = None
    movie_rating: Optional[RatingPercentages] = None

class MoviesInResponse(BaseSchemaModel):
    movies: List[MovieInResponse]