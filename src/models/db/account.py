import datetime
from typing import List

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped as SQLAlchemyMapped, mapped_column as sqlalchemy_mapped_column, relationship, Mapped, \
    backref
from sqlalchemy.sql import functions as sqlalchemy_functions

from src.models.db.wallet import Wallet
from src.repository.table import Base


class Account(Base):  # type: ignore
    __tablename__ = "account"

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement="auto")
    profile_image: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=1024), nullable=False, default="https://ewr1.vultrobjects.com/cinegrade/default_pic.png")
    username: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(
        sqlalchemy.String(length=64), nullable=False, unique=True
    )
    email: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False, unique=True)
    _hashed_password: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=1024), nullable=True)
    _hash_salt: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=1024), nullable=True)
    is_verified: SQLAlchemyMapped[bool] = sqlalchemy_mapped_column(sqlalchemy.Boolean, nullable=False, default=False)
    is_active: SQLAlchemyMapped[bool] = sqlalchemy_mapped_column(sqlalchemy.Boolean, nullable=False, default=False)
    is_logged_in: SQLAlchemyMapped[bool] = sqlalchemy_mapped_column(sqlalchemy.Boolean, nullable=False, default=False)
    created_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True), nullable=False, server_default=sqlalchemy_functions.now()
    )
    updated_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
        server_onupdate=sqlalchemy.schema.FetchedValue(for_update=True),
    )
    is_test_account: SQLAlchemyMapped[bool] = sqlalchemy_mapped_column(sqlalchemy.Boolean, nullable=False, default=False)
    registration_ip: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=15), nullable=True)
    current_ip: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=15), nullable=True)
    is_proxy: SQLAlchemyMapped[bool] = sqlalchemy_mapped_column(sqlalchemy.Boolean, nullable=False, default=False)
    ip_location: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=True)
    miners: Mapped[List["Miner"]] = relationship("Miner", back_populates="account")
    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="account", uselist=False, cascade="all, delete", passive_deletes=True)
    reviews: SQLAlchemyMapped["Reviews"] = relationship("Reviews", back_populates="account", cascade="all, delete", passive_deletes=True)
    tasks: SQLAlchemyMapped[List["Task"]] = relationship("Task", back_populates="account", cascade="all, delete", passive_deletes=True)
    uploaded_movies: SQLAlchemyMapped[List["Movie"]] = relationship("Movie", back_populates="account")
    is_admin: SQLAlchemyMapped[bool] = sqlalchemy_mapped_column(sqlalchemy.Boolean, nullable=False, default=False)
    level: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False, default=1)

    __mapper_args__ = {"eager_defaults": True}

    @property
    def hashed_password(self) -> str:
        return self._hashed_password

    def set_hashed_password(self, hashed_password: str) -> None:
        self._hashed_password = hashed_password

    @property
    def hash_salt(self) -> str:
        return self._hash_salt

    def set_hash_salt(self, hash_salt: str) -> None:
        self._hash_salt = hash_salt


class Referal(Base):
    __tablename__ = "referal"

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement="auto")
    referal_code: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False, unique=True)


class CustomerService(Base):
    __tablename__ = "customer_service"

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement="auto")
    whatsapp: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False,default="https://wa.me/14383408868")


