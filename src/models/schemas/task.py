import datetime
from typing import Optional

from src.models.schemas.base import BaseSchemaModel

class TaskCategoryBase(BaseSchemaModel):
    name: str
    description: str
    access_level: int
    movies_uploaded_count: int
    reviews_posted_count: int
    total_movies_uploaded: int
    total_reviews_posted: int
    task_reward: float

class TaskCategoryInCreate(TaskCategoryBase):
    pass

class TaskCategoryInResponse(TaskCategoryBase):
    pass

class TaskBase(BaseSchemaModel):
    task_category: TaskCategoryInResponse
    is_completed: bool
    is_claimed: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime | None

class TaskInCreate(TaskBase):
    pass
class TaskInResponse(TaskBase):
    id: int
    movies_uploaded_since_task_start: int
    reviews_posted_since_task_start: int
    progress: Optional[float] = None

class TaskInAssign(BaseSchemaModel):
    account_id: int
    task_level: int
