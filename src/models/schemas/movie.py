import datetime
from typing import List, Optional

from pydantic import HttpUrl
from pydantic.v1 import root_validator

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
    title: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[str] = None
    genre: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[str] = None
    duration: Optional[int] = None
    cover_image_url: Optional[HttpUrl] = None

class MovieInCreate(MovieBase):
    imdb_url: Optional[str] = None

    @root_validator(pre=True)  # pre=True to run this validator before others
    def check_imdb_url(cls, values):
        imdb_url = values.get('imdb_url')
        if imdb_url:
            # If imdb_url is provided, set other fields to None or default values
            for field in values:
                if field != 'imdb_url':
                    values[field] = None
        return values



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