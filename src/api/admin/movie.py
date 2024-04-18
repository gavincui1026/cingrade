import fastapi

from src.api.dependencies.repository import get_repository
from src.models.schemas.movie import MovieInResponse, AdminMovieInResponse
from src.repository.crud.movie import MovieCRUDRepository

router = fastapi.APIRouter(prefix="/movies")

@router.get(
    path="review-movies",
    name="movies:review-movies",
    response_model=list[AdminMovieInResponse],
    status_code=fastapi.status.HTTP_200_OK,
    description="读取所有待审核的电影"
)
async def review_movies(
    movie_repo: MovieCRUDRepository = fastapi.Depends(get_repository(repo_type=MovieCRUDRepository)),
) -> list[AdminMovieInResponse]:
    db_movies = await movie_repo.read_all()
    db_movie_list: list = list()

    for db_movie in db_movies:
        movie = AdminMovieInResponse(
            id=db_movie.id,
            title=db_movie.title,
            description=db_movie.description,
            year=db_movie.year,
            rating=db_movie.rating,
            genre=db_movie.genre,
            director=db_movie.director,
            cast=db_movie.cast,
            duration=db_movie.duration,
            cover_image_url=db_movie.cover_image_url,
            account_id=db_movie.account_id,
            is_verified=db_movie.is_verified,
        )
        db_movie_list.append(movie)

    return db_movie_list

@router.post(
    path="approve-movies",
    name="movies:approve-movies",
    response_model=AdminMovieInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
    description="批准电影"
)
async def approve_movies(
        movie_ids: list[int],
        movie_repo: MovieCRUDRepository = fastapi.Depends(get_repository(repo_type=MovieCRUDRepository)),
) -> AdminMovieInResponse:
    # db_movie = await movie_repo.approve_movies(movie_ids=movie_ids)
    # return db_movie
    pass
