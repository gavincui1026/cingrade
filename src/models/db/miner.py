import datetime
from typing import List

import sqlalchemy
from sqlalchemy.orm import Mapped as SQLAlchemyMapped, mapped_column as sqlalchemy_mapped_column, relationship, Mapped
from sqlalchemy.sql import functions as sqlalchemy_functions

from src.repository.table import Base

class MinerConfig(Base):
    __tablename__ = "miner_config"
    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement="auto")
    algorithm: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False, default="SHA-256")
    hashpower: SQLAlchemyMapped[float] = sqlalchemy_mapped_column(sqlalchemy.Float, nullable=False)
    name:SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    price:SQLAlchemyMapped[float] = sqlalchemy_mapped_column(sqlalchemy.Float, nullable=False)
    miners: Mapped[List["Miner"]] = relationship("Miner", back_populates="config")

    __mapper_args__ = {"eager_defaults": True}

class Miner(Base):
    __tablename__ = "miner"
    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement="auto")
    config_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("miner_config.id"))
    config : Mapped["MinerConfig"] = relationship("MinerConfig", back_populates="miners")
    user_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("account.id"))
    account: Mapped["Account"] = relationship("Account", back_populates="miners")
    created_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True), nullable=False, server_default=sqlalchemy_functions.now()
    )
    updated_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
        server_onupdate=sqlalchemy.schema.FetchedValue(for_update=True),
    )

    __mapper_args__ = {"eager_defaults": True}


