import typing

import sqlalchemy

from src.models.db.movie import Movie, Reviews, SearchingPage, HomePage, JustReviewed
from src.models.schemas.movie import MovieInCreate, ReviewInCreate, RatingPercentages
from src.repository.crud.base import BaseCRUDRepository
from src.utilities.exceptions.database import EntityDoesNotExist, EntityAlreadyExists
from src.utilities.imdb_scraper.imdb import async_get_by_id


class MovieCRUDRepository(BaseCRUDRepository):
    async def create_movie(self, movie: MovieInCreate,account_id: int) -> Movie:
        if movie.imdb_url:
            # 如果提供了IMDb URL，则使用IMDb Scraper从IMDb获取电影信息
            result = await async_get_by_id(imdb_url=movie.imdb_url)
            new_movie = Movie(
                title=result.get('name'),
                description=result.get('description'),
                # year需要是整数类型
                year=int(result.get('datePublished').split('-')[0]),
                rating=result.get('ContentRating'),
                genre=', '.join(result.get('genre')),
                director=', '.join([director.get('name') for director in result.get('director')]),
                cast=', '.join([actor.get('name') for actor in result.get('actor')]),
                duration=result.get('duration'),
                cover_image_url=result.get('poster'),
                account_id=account_id
            )
        else:
            new_movie = Movie(
                title=movie.title,
                description=movie.description,
                year=movie.year,
                rating=movie.rating,
                genre=movie.genre,
                director=movie.director,
                cast=movie.cast,
                duration=movie.duration,
                cover_image_url=movie.cover_image_url,
                account_id=account_id
            )
        try:
            await self.is_movie_title_taken(title=new_movie.title)
        except EntityAlreadyExists:
            raise EntityAlreadyExists(f"Movie with title `{new_movie.title}` already exists!")
        self.async_session.add(instance=new_movie)
        await self.async_session.commit()
        await self.async_session.refresh(instance=new_movie)
        return new_movie

    async def create_review(self, review: ReviewInCreate, account_id: int) -> Reviews:
        new_review = Reviews(
            movie_id=review.movie_id,
            account_id=account_id,
            review=review.review,
            rating=review.rating,
        )
        self.async_session.add(instance=new_review)
        await self.async_session.commit()
        await self.async_session.refresh(instance=new_review)
        return new_review

    async def read_movie_by_id(self, id: int) -> Movie:
        stmt = sqlalchemy.select(Movie).options(sqlalchemy.orm.joinedload(Movie.reviews).joinedload(Reviews.account)).where(Movie.id == id)
        query = await self.async_session.execute(statement=stmt)

        if not query:
            raise EntityDoesNotExist(f"Movie with id `{id}` does not exist!")

        return query.scalar()

    async def read_all(self,page) -> typing.Sequence[Movie]:
        stmt = sqlalchemy.select(Movie).limit(10).offset((page-1)*10)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()

    async def session_update(self, movie: Movie):
        await self.async_session.refresh(instance=movie)
        return movie

    async def is_movie_title_taken(self, title: str):
        stmt = sqlalchemy.select(Movie).where(Movie.title == title)
        query = await self.async_session.execute(statement=stmt)
        movie = query.scalar()
        if movie:
            raise EntityAlreadyExists(f"Movie with title `{title}` already exists!")
        return movie

    async def calculate_rates_in_percentage(self, reviews):
        # 初始化评级计数器
        ratings_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        # 计数每个评级的出现次数
        for review in reviews:
            if 1 <= review.rating <= 5:
                if review.rating not in ratings_count:
                    ratings_count[review.rating] = 0
                ratings_count[review.rating] += 1

        # 计算总评论数
        total_reviews = len(reviews)

        # 避免除以零的错误
        if total_reviews == 0:
            return RatingPercentages(
                average_rating=0.0,
                rating_1=0.0,
                rating_2=0.0,
                rating_3=0.0,
                rating_4=0.0,
                rating_5=0.0
            )

        # 计算每个评级的百分比
        ratings_percentage = {rating: (count / total_reviews) * 100 for rating, count in ratings_count.items()}

        # 计算平均评分
        average_rating = sum(rating * count for rating, count in ratings_count.items()) / total_reviews

        # 创建并返回RatingPercentages实例
        return RatingPercentages(
            average_rating=average_rating,
            rating_1=ratings_percentage[1],
            rating_2=ratings_percentage[2],
            rating_3=ratings_percentage[3],
            rating_4=ratings_percentage[4],
            rating_5=ratings_percentage[5]
        )

    async def read_movies_sorted_by_year(self, page: int, order: str) -> typing.Sequence[Movie]:
        if order.lower() == 'asc':
            order_by_clause = Movie.year.asc()
        else:
            order_by_clause = Movie.year.desc()
        stmt = sqlalchemy.select(Movie).order_by(order_by_clause).limit(10).offset((page-1)*10)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()

    async def read_movies_sorted_by_rating(self, page: int, order: str, page_size: int = 10) -> typing.Sequence[Movie]:
        # 构造一个查询，计算每部电影的平均评分，并按此排序
        if order.lower() == 'asc':
            order_by_clause = sqlalchemy.func.coalesce(sqlalchemy.func.avg(Reviews.rating), 0).asc()
        else:
            order_by_clause = sqlalchemy.func.coalesce(sqlalchemy.func.avg(Reviews.rating), 0).desc()
        stmt = (
            sqlalchemy.select(Movie)
            .outerjoin(Reviews, Movie.id == Reviews.movie_id)  # 使用外连接包括未被评价的电影
            .group_by(Movie.id)
            .order_by(order_by_clause)  # 使用coalesce处理未被评价的电影
            .limit(page_size)
            .offset(page_size * (page - 1))
            .options(sqlalchemy.orm.joinedload(Movie.reviews))  # 可选，如果你在结果中需要访问具体的评价信息
        )

        results = await self.async_session.execute(stmt)
        movies = results.scalars().unique().all()
        return movies

    async def search_movie(self, search: str, page_size: int = 10, page_num: int = 1) -> typing.Sequence[Movie]:
        stmt = sqlalchemy.select(Movie).where(Movie.title.ilike(f"%{search}%")).limit(page_size).offset((page_num - 1) * page_size)
        query = await self.async_session.execute(stmt)
        return query.scalars().all()

    async def read_movies_by_genre(self, genre: str) -> typing.Sequence[Movie]:
        stmt = sqlalchemy.select(Movie).where(Movie.genre.ilike(f"%{genre}%"))
        query = await self.async_session.execute(stmt)
        return query.scalars().all()

    async def read_movies_of_searching_page(self):
        stmt = sqlalchemy.select(SearchingPage).options(sqlalchemy.orm.joinedload(SearchingPage.movie))
        query = await self.async_session.execute(stmt)
        return query.scalars().all()

    async def read_movies_of_home_page(self):
        stmt = sqlalchemy.select(HomePage).options(sqlalchemy.orm.joinedload(HomePage.movie))
        query = await self.async_session.execute(stmt)
        return query.scalars().all()

    async def read_movies_of_just_reviewed(self):
        stmt = sqlalchemy.select(JustReviewed).options(sqlalchemy.orm.joinedload(JustReviewed.movie))
        query = await self.async_session.execute(stmt)
        return query.scalars().all()





