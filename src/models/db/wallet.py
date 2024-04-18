import datetime
from typing import List

import sqlalchemy
from sqlalchemy.orm import Mapped as SQLAlchemyMapped, mapped_column as sqlalchemy_mapped_column, relationship, Mapped
from sqlalchemy.sql import functions as sqlalchemy_functions

from src.repository.table import Base

class Wallet(Base):
    __tablename__ = "wallet"
    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement="auto")
    bitcoin_address: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=True)
    usdt_address: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=True)
    ethereum_address: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=True)
    tron_address: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=True)
    balance: SQLAlchemyMapped[float] = sqlalchemy_mapped_column(sqlalchemy.Float, nullable=False, server_default="0")
    transactions: Mapped[List["Transactions"]] = relationship("Transactions", back_populates="wallet")
    account_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("account.id"))
    account: Mapped["Account"] = relationship("Account", back_populates="wallet", uselist=False)

    __mapper_args__ = {"eager_defaults": True}

class Transactions(Base):
    __tablename__ = "transactions"
    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement="auto")
    wallet_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("wallet.id"))
    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="transactions", uselist=False)
    amount: SQLAlchemyMapped[float] = sqlalchemy_mapped_column(sqlalchemy.Float, nullable=False)
    created_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True), nullable=False, server_default=sqlalchemy_functions.now()
    )
    updated_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
        server_onupdate=sqlalchemy.schema.FetchedValue(for_update=True),
    )
    transaction_type: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    transaction_status: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    transaction_currency: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    order_id: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    payment_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=True)

    __mapper_args__ = {"eager_defaults": True}