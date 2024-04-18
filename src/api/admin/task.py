
import fastapi


from src.api.dependencies.repository import get_repository
from src.models.schemas.task import TaskInResponse, TaskInAssign, TaskCategoryInResponse, TaskCategoryInCreate
from src.repository.crud.task import TaskCrudRepository

router = fastapi.APIRouter(prefix="/task")

@router.post(
    path="/assign-task",
    name="task:assign-task",
    status_code=fastapi.status.HTTP_200_OK,
    description="分配任务,用于管理员分配任务",
)
async def assign_task(
    task: TaskInAssign,
    task_repo: TaskCrudRepository = fastapi.Depends(get_repository(repo_type=TaskCrudRepository)),
) -> fastapi.Response:
    new_task = await task_repo.assign_task(account_id=task.account_id, task_level=task.task_level)
    return fastapi.Response(status_code=fastapi.status.HTTP_200_OK, content=f"Task assigned to account {task.account_id}")

@router.get(
    path="/get-tasks",
    name="task:get-tasks",
    response_model=list[TaskCategoryInResponse],
    status_code=fastapi.status.HTTP_200_OK,
    description="获取任务种类,用于管理员查看任务种类",
)
async def get_task_categories(
    task_repo: TaskCrudRepository = fastapi.Depends(get_repository(repo_type=TaskCrudRepository)),
) -> list[TaskCategoryInResponse]:
    db_task_categories = await task_repo.read_task_categories()
    task_categories=[]
    for task in db_task_categories:
        task_categories.append(
            TaskCategoryInResponse(
                id=task.id,
                name=task.name,
                description=task.description,
                access_level=task.access_level,
                movies_uploaded_count=task.movies_uploaded_count,
                reviews_posted_count=task.reviews_posted_count,
                total_movies_uploaded=task.total_movies_uploaded,
                total_reviews_posted=task.total_reviews_posted,
                task_reward=task.task_reward,
            )
        )
    return task_categories

@router.post(
    path="/create-task",
    name="task:create-task",
    response_model=TaskCategoryInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
    description="创建任务种类，用于管理员创建任务种类",
)
async def create_task_categories(
    task: TaskCategoryInCreate,
    task_repo: TaskCrudRepository = fastapi.Depends(get_repository(repo_type=TaskCrudRepository)),
) -> TaskCategoryInResponse:
    new_task = await task_repo.create_task_category(task_category=task)
    return TaskCategoryInResponse(
        id=new_task.id,
        name=new_task.name,
        description=new_task.description,
        access_level=new_task.access_level,
        movies_uploaded_count=new_task.movies_uploaded_count,
        reviews_posted_count=new_task.reviews_posted_count,
        total_movies_uploaded=new_task.total_movies_uploaded,
        total_reviews_posted=new_task.total_reviews_posted,
        task_reward=new_task.task_reward,
    )