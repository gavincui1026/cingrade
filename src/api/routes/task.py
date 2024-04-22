import typing

import fastapi

from src.api.dependencies.repository import get_repository
from src.api.dependencies.token import get_user_me
from src.models.schemas.task import TaskCategoryInResponse, TaskInResponse
from src.repository.crud.task import TaskCrudRepository

router = fastapi.APIRouter(prefix="/task", tags=["task"])




@router.get(
    path="/read-tasks",
    name="task:read-tasks",
    response_model=list[TaskInResponse],
    description="获取任务,用于用户查看任务",
)
async def read_tasks(
    task_repo: TaskCrudRepository = fastapi.Depends(get_repository(repo_type=TaskCrudRepository)),
    user=fastapi.Depends(get_user_me),
) -> list[TaskInResponse]:
    db_tasks = await task_repo.read_tasks_by_account_id(account_id=user.id)
    tasks=[]
    for task in db_tasks:
        tasks.append(
            TaskInResponse(
                id=task.id,
                task_category=TaskCategoryInResponse(
                    id=task.task_category.id,
                    name=task.task_category.name,
                    description=task.task_category.description,
                    access_level=task.task_category.access_level,
                    movies_uploaded_count=task.task_category.movies_uploaded_count,
                    reviews_posted_count=task.task_category.reviews_posted_count,
                    total_movies_uploaded=task.task_category.total_movies_uploaded,
                    total_reviews_posted=task.task_category.total_reviews_posted,
                    task_reward=task.task_category.task_reward,
                ),
                is_completed=task.is_completed,
                is_claimed=task.is_claimed,
                created_at=task.created_at,
                updated_at=task.updated_at,
                movies_uploaded_since_task_start=task.movies_uploaded_since_task_start,
                reviews_posted_since_task_start=task.reviews_posted_since_task_start,
                progress=task_repo.calculate_weighted_progress(task.movies_uploaded_since_task_start,
                                                               task.reviews_posted_since_task_start,
                                                               task.task_category.movies_uploaded_count,
                                                               task.task_category.reviews_posted_count)
            )
        )
    return tasks

@router.get(
    path="/claim-reward",
    name="task:claim-reward",
    response_model=TaskInResponse,
    status_code=fastapi.status.HTTP_200_OK,
    description="领取任务奖励",
)
async def claim_reward(
    task_id: int,
    task_repo: TaskCrudRepository = fastapi.Depends(get_repository(repo_type=TaskCrudRepository)),
    user=fastapi.Depends(get_user_me),
) -> TaskInResponse:
    task = await task_repo.claim_task_reward(task_id=task_id, account_id=user.id)
    return TaskInResponse(
        id=task.id,
        task_category=TaskCategoryInResponse(
            id=task.task_category.id,
            name=task.task_category.name,
            description=task.task_category.description,
            access_level=task.task_category.access_level,
            movies_uploaded_count=task.task_category.movies_uploaded_count,
            reviews_posted_count=task.task_category.reviews_posted_count,
            total_movies_uploaded=task.task_category.total_movies_uploaded,
            total_reviews_posted=task.task_category.total_reviews_posted,
            task_reward=task.task_category.task_reward,
        ),
        is_completed=task.is_completed,
        is_claimed=task.is_claimed,
        created_at=task.created_at,
        updated_at=task.updated_at,
        movies_uploaded_since_task_start=task.movies_uploaded_since_task_start,
        reviews_posted_since_task_start=task.reviews_posted_since_task_start,
        progress=task_repo.calculate_weighted_progress(task.movies_uploaded_since_task_start,
                                                       task.reviews_posted_since_task_start,
                                                       task.task_category.movies_uploaded_count,
                                                       task.task_category.reviews_posted_count)

    )
