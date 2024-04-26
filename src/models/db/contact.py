import sqlalchemy
from src.repository.table import Base
from sqlalchemy.orm import Mapped as SQLAlchemyMapped, mapped_column as sqlalchemy_mapped_column, relationship, Mapped, \
    backref

class Contact(Base):  # type: ignore
    __tablename__ = "contact"

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement="auto")
    name: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=True)
    email: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=True)
    calling_code: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=6), nullable=True)
    phone: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=15), nullable=True)
    message: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=1024), nullable=True)
    ip: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=15), nullable=False)
    country_name: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    country_code: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=2), nullable=False)
    region_name: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    city: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    uuid: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)

