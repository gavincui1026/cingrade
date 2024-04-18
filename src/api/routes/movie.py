import fastapi
from fastapi import HTTPException

from src.api.dependencies.repository import get_repository
from src.api.dependencies.token import get_user_me
from src.models.schemas.movie import MovieInCreate, MovieInResponse, ReviewInResponse, ReviewInCreate, MoviesInResponse
from src.repository.crud.movie import MovieCRUDRepository
from src.repository.crud.task import TaskCrudRepository
from src.utilities.exceptions.database import EntityAlreadyExists

router = fastapi.APIRouter(prefix="/movie", tags=["movie"])
@router.post(
    path="/create-movie",
    name="movie:create-movie",
    response_model=MovieInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def create_movie(
    movie: MovieInCreate,
    movie_repo: MovieCRUDRepository = fastapi.Depends(get_repository(repo_type=MovieCRUDRepository)),
    task_repo: TaskCrudRepository = fastapi.Depends(get_repository(repo_type=TaskCrudRepository)),
    user=fastapi.Depends(get_user_me),
) -> MovieInResponse:
    try:
        await movie_repo.is_movie_title_taken(title=movie.title)
    except EntityAlreadyExists:
        raise HTTPException(status_code=400, detail=f"Movie {movie.title} already exists")
    new_movie = await movie_repo.create_movie(movie=movie, account_id=user.id)
    await task_repo.add_movie_uploaded_count(account_id=new_movie.account_id)
    new_movie= await movie_repo.session_update(movie=new_movie)
    return MovieInResponse(
        id=new_movie.id,
        title=new_movie.title,
        description=new_movie.description,
        year=new_movie.year,
        rating=new_movie.rating,
        genre=new_movie.genre,
        director=new_movie.director,
        cast=new_movie.cast,
        duration=new_movie.duration,
        cover_image_url=new_movie.cover_image_url,
        reviews=[],
    )
@router.post(
    path="/create-review",
    name="movie:create-review",
    response_model=MovieInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def create_review(
    review: ReviewInCreate,
    movie_repo: MovieCRUDRepository = fastapi.Depends(get_repository(repo_type=MovieCRUDRepository)),
    task_repo: TaskCrudRepository = fastapi.Depends(get_repository(repo_type=TaskCrudRepository)),
    user=fastapi.Depends(get_user_me),
) -> MovieInResponse:
    user_id = user.id
    new_review = await movie_repo.create_review(review=review, account_id=user_id)
    movie = await movie_repo.read_movie_by_id(id=new_review.movie_id)
    await task_repo.add_review_posted_count(account_id=user_id)
    movie = await movie_repo.session_update(movie=movie)
    reviews = []
    for review in movie.reviews:
        reviews.append(
            ReviewInResponse(
                id=review.id,
                movie_id=review.movie_id,
                account_id=review.account_id,
                review=review.review,
                rating=review.rating,
                created_at=review.created_at,
                updated_at=review.updated_at,
                profile_picture=review.account.profile_image,
                username=review.account.username,
            )
        )
    return MovieInResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        year=movie.year,
        rating=movie.rating,
        genre=movie.genre,
        director=movie.director,
        cast=movie.cast,
        duration=movie.duration,
        cover_image_url=movie.cover_image_url,
        reviews=reviews,
    )

@router.get(
    path="/get-movies",
    name="movie:get-movies",
    response_model=MoviesInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_movies(
    movie_repo: MovieCRUDRepository = fastapi.Depends(get_repository(repo_type=MovieCRUDRepository)),
    page: int = 1,
) -> MoviesInResponse:
    movies = await movie_repo.read_all(page=page)
    movie_list = []
    for movie in movies:
        movie_list.append(
            MovieInResponse(
                id=movie.id,
                title=movie.title,
                description=movie.description,
                year=movie.year,
                rating=movie.rating,
                genre=movie.genre,
                director=movie.director,
                cast=movie.cast,
                duration=movie.duration,
                cover_image_url=movie.cover_image_url,
            )
        )
    return MoviesInResponse(movies=movie_list)
@router.get(
    path="/get_movies_sorted_by_year",
    name="movie:get_movies_sorted_by_year",
    response_model=MoviesInResponse,
    status_code=fastapi.status.HTTP_200_OK,
    description="按年份排序的电影",
)
async def get_movies_sorted_by_year(
    movie_repo: MovieCRUDRepository = fastapi.Depends(get_repository(repo_type=MovieCRUDRepository)),
        page: int = 1,
        order: str = "asc",
) -> MoviesInResponse:
    movies = await movie_repo.read_movies_sorted_by_year(page, order)
    movie_list = []
    for movie in movies:
        movie_list.append(
            MovieInResponse(
                id=movie.id,
                title=movie.title,
                description=movie.description,
                year=movie.year,
                rating=movie.rating,
                genre=movie.genre,
                director=movie.director,
                cast=movie.cast,
                duration=movie.duration,
                cover_image_url=movie.cover_image_url,
            )
        )
    return MoviesInResponse(movies=movie_list)

@router.get(
    path="/get_movies_sorted_by_rating",
    name="movie:get_movies_sorted_by_rating",
    response_model=MoviesInResponse,
    status_code=fastapi.status.HTTP_200_OK,
    description="按评分排序的电影",
)
async def get_movies_sorted_by_rating(
    movie_repo: MovieCRUDRepository = fastapi.Depends(get_repository(repo_type=MovieCRUDRepository)),
    page: int = 1,
    rating: str = "asc",
) -> MoviesInResponse:
    movies = await movie_repo.read_movies_sorted_by_rating(page, rating)
    movie_list = []
    for movie in movies:
        movie_list.append(
            MovieInResponse(
                id=movie.id,
                title=movie.title,
                description=movie.description,
                year=movie.year,
                rating=movie.rating,
                genre=movie.genre,
                director=movie.director,
                cast=movie.cast,
                duration=movie.duration,
                cover_image_url=movie.cover_image_url,
            )
        )
    return MoviesInResponse(movies=movie_list)

@router.get(
    path="/get-movie/{id}",
    name="movie:get-movie",
    response_model=MovieInResponse,
    status_code=fastapi.status.HTTP_200_OK,
    description="单个电影页面",
)
async def get_movie_by_id(
    id: int,
    movie_repo: MovieCRUDRepository = fastapi.Depends(get_repository(repo_type=MovieCRUDRepository)),
) -> MovieInResponse:
    movie = await movie_repo.read_movie_by_id(id=id)
    reviews = []
    for review in movie.reviews:
        reviews.append(
            ReviewInResponse(
                id=review.id,
                movie_id=review.movie_id,
                account_id=review.account_id,
                review=review.review,
                rating=review.rating,
                created_at=review.created_at,
                updated_at=review.updated_at,
                profile_picture=review.account.profile_image,
                username=review.account.username,
            )
        )
    rating_percentages = await movie_repo.calculate_rates_in_percentage(reviews=reviews)
    return MovieInResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        year=movie.year,
        rating=movie.rating,
        genre=movie.genre,
        director=movie.director,
        cast=movie.cast,
        duration=movie.duration,
        cover_image_url=movie.cover_image_url,
        reviews=reviews,
        movie_rating=rating_percentages,
    )

