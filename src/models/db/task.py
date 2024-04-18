import datetime
from typing import Sequence, List

import sqlalchemy
from sqlalchemy import event

from src.repository.table import Base

from sqlalchemy.orm import Mapped as SQLAlchemyMapped, mapped_column as sqlalchemy_mapped_column, relationship

from sqlalchemy.sql import functions as sqlalchemy_functions

class TaskCategory(Base):
    __tablename__ = 'task_categories'

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement=True)
    name: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=64), nullable=False)
    description: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=512), nullable=False)
    access_level: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False)
    movies_uploaded_count: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False)
    reviews_posted_count: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False)
    total_movies_uploaded: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False)
    total_reviews_posted: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False)
    task_reward: SQLAlchemyMapped[float] = sqlalchemy_mapped_column(sqlalchemy.Float, nullable=False)
    tasks: SQLAlchemyMapped[List["Task"]] = relationship("Task", back_populates="task_category")
class Task(Base):
    __tablename__ = 'tasks'

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement=True)
    task_category_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("task_categories.id"))
    task_category: SQLAlchemyMapped["TaskCategory"] = relationship("TaskCategory", back_populates="tasks")
    is_completed: SQLAlchemyMapped[bool] = sqlalchemy_mapped_column(sqlalchemy.Boolean, nullable=False, server_default=sqlalchemy.sql.expression.false())
    account_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, sqlalchemy.ForeignKey("account.id"))
    account: SQLAlchemyMapped["Account"] = relationship("Account", back_populates="tasks")
    created_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True), nullable=False, server_default=sqlalchemy_functions.now()
    )
    updated_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
        server_onupdate=sqlalchemy.schema.FetchedValue(for_update=True),
    )
    movies_uploaded_since_task_start: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False, server_default="0")
    reviews_posted_since_task_start: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False, server_default="0")
    is_claimed: SQLAlchemyMapped[bool] = sqlalchemy_mapped_column(sqlalchemy.Boolean, nullable=False, server_default=sqlalchemy.sql.expression.false())

    __mapper_args__ = {"eager_defaults": True}

def check_task_completion(target, value, oldvalue, initiator):
    if (target.movies_uploaded_since_task_start >= target.task_category.movies_uploaded_count and
        target.reviews_posted_since_task_start >= target.task_category.reviews_posted_count):
        target.is_completed = True

event.listen(Task.movies_uploaded_since_task_start, 'set', check_task_completion)