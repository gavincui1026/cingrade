import datetime
from typing import List

import sqlalchemy

from src.repository.table import Base

from sqlalchemy.orm import Mapped as SQLAlchemyMapped, mapped_column as sqlalchemy_mapped_column, relationship

from sqlalchemy.sql import functions as sqlalchemy_functions

class Movie(Base):
    __tablename__ = 'movies'

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement=True)
    title: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    description: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.Text, nullable=False)
    year: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False)
    rating: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=128), nullable=False)
    genre: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=255), nullable=False)
    director: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    cast: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.Text, nullable=False)
    duration: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False)
    cover_image_url: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.Text, nullable=False)
    reviews: SQLAlchemyMapped[List["Reviews"]] = relationship("Reviews", back_populates="movie", cascade="all, delete", passive_deletes=True)
    is_verified: SQLAlchemyMapped[bool] = sqlalchemy_mapped_column(sqlalchemy.Boolean, nullable=False, server_default=sqlalchemy.sql.expression.false())
    account_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("account.id"))
    account: SQLAlchemyMapped["Account"] = relationship("Account", back_populates="uploaded_movies")
    general_category: SQLAlchemyMapped["str"] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=True)
    homepage: SQLAlchemyMapped["HomePage"] = relationship("HomePage", back_populates="movie", uselist=False)
    searchingpage: SQLAlchemyMapped["SearchingPage"] = relationship("SearchingPage", back_populates="movie", uselist=False)
    justreviewed: SQLAlchemyMapped["JustReviewed"] = relationship("JustReviewed", back_populates="movie", uselist=False)

    __mapper_args__ = {"eager_defaults": True}

class Reviews(Base):
    __tablename__ = 'reviews'

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement=True)
    movie_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("movies.id", ondelete="CASCADE"))
    account_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("account.id"))
    review: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=512), nullable=False)
    rating: SQLAlchemyMapped[float] = sqlalchemy_mapped_column(sqlalchemy.Float, nullable=False)
    created_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True), nullable=False, server_default=sqlalchemy_functions.now()
    )
    updated_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
        server_onupdate=sqlalchemy.schema.FetchedValue(for_update=True),
    )
    movie: SQLAlchemyMapped["Movie"] = relationship("Movie", back_populates="reviews")
    account: SQLAlchemyMapped["Account"] = relationship("Account", back_populates="reviews")

    __mapper_args__ = {"eager_defaults": True}

class HomePage(Base):
    __tablename__ = 'homepage'

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement=True)
    movie_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("movies.id", ondelete="CASCADE"))
    movie: SQLAlchemyMapped["Movie"] = relationship("Movie", back_populates="homepage")

    __mapper_args__ = {"eager_defaults": True}

class SearchingPage(Base):
    __tablename__ = 'searchingpage'

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement=True)
    movie_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("movies.id", ondelete="CASCADE"))
    movie: SQLAlchemyMapped["Movie"] = relationship("Movie", back_populates="searchingpage")

    __mapper_args__ = {"eager_defaults": True}

class JustReviewed(Base):
    __tablename__ = 'justreviewed'

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement=True)
    movie_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("movies.id", ondelete="CASCADE"))
    movie: SQLAlchemyMapped["Movie"] = relationship("Movie", back_populates="justreviewed")

    __mapper_args__ = {"eager_defaults": True}
