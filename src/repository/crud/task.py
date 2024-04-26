import typing

import sqlalchemy
from fastapi import HTTPException

from src.models.db.account import Account
from src.models.db.task import TaskCategory, Task
from src.models.schemas.task import TaskCategoryInCreate
from src.repository.crud.base import BaseCRUDRepository

class TaskCrudRepository(BaseCRUDRepository):
    async def create_task_category(self, task_category: TaskCategoryInCreate) -> TaskCategory:
        db_task_category = TaskCategory(
            name=task_category.name,
            description=task_category.description,
            access_level=task_category.access_level,
            movies_uploaded_count=task_category.movies_uploaded_count,
            reviews_posted_count=task_category.reviews_posted_count,
            total_movies_uploaded=task_category.total_movies_uploaded,
            total_reviews_posted=task_category.total_reviews_posted,
            task_reward=task_category.task_reward
        )
        self.async_session.add(instance=db_task_category)
        await self.async_session.commit()
        await self.async_session.refresh(instance=db_task_category)
        return db_task_category
    async def read_task_categories(self) -> typing.Sequence[TaskCategory]:
        stmt = sqlalchemy.select(TaskCategory)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()
    async def read_task_categories_by_access_level(self, access_level: int) -> typing.Sequence[TaskCategory]:
        stmt = sqlalchemy.select(TaskCategory).where(TaskCategory.access_level == access_level)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()

    async def read_task_category_by_id(self, id: int) -> TaskCategory:
        stmt = sqlalchemy.select(TaskCategory).where(TaskCategory.id == id)
        query = await self.async_session.execute(statement=stmt)
        return query.scalar()
    async def apply_default_tasks(self, account_id: int)-> typing.Sequence[Task]:
        task_categories = await self.read_task_categories_by_access_level(access_level=1)
        tasks = []
        for task_category in task_categories:
            db_task = Task(
                task_category_id=task_category.id,
                account_id=account_id,
            )
            self.async_session.add(instance=db_task)
            tasks.append(db_task)
        await self.async_session.commit()
        return tasks

    async def read_tasks(self) -> typing.Sequence[Task]:
        stmt = sqlalchemy.select(Task)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()

    async def read_tasks_by_account_id(self, account_id: int) -> typing.Sequence[Task]:
        stmt = sqlalchemy.select(Task).options(sqlalchemy.orm.joinedload(Task.task_category)).where(Task.account_id == account_id)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()

    async def update_task_status(self, task: Task) -> Task:
        # 检查电影上传和评论发布是否达到了任务类别要求的数量
        basic_conditions_met = (
                task.movies_uploaded_since_task_start >= task.task_category.movies_uploaded_count and
                task.reviews_posted_since_task_start >= task.task_category.reviews_posted_count
        )

        # 检查是否需要版权，并且如果需要，是否已经获得
        copyright_condition_met = (
                not task.task_category.is_copy_right_required or
                (task.task_category.is_copy_right_required and task.is_copy_right_acquired)
        )

        # 仅当所有条件都满足时，将任务标记为已完成
        if basic_conditions_met and copyright_condition_met:
            task.is_completed = True

        return task



    async def add_movie_uploaded_count(self, account_id: int) -> typing.Sequence[Task]:
        # 查询账户的所有任务，预加载必要的关联数据
        select_stmt = sqlalchemy.select(Task).options(
            sqlalchemy.orm.joinedload(Task.task_category),
            sqlalchemy.orm.joinedload(Task.account).joinedload(Account.wallet)
        ).where(
            Task.account_id == account_id,
            Task.is_completed == False
        )

        result = await self.async_session.execute(select_stmt)
        tasks = result.scalars().all()

        # 对每个任务进行处理，只增加那些未达到上传次数上限的任务的上传计数
        for task in tasks:
            if task.movies_uploaded_since_task_start < task.task_category.movies_uploaded_count:
                task.movies_uploaded_since_task_start += 1
                # 检查任务是否满足完成条件
                task = await self.update_task_status(task)

        # 提交所有更改
        await self.async_session.commit()

        return tasks

    async def add_review_posted_count(self, account_id: int) -> typing.Sequence[Task]:
        # 查询账户的所有任务，预加载必要的关联数据
        select_stmt = sqlalchemy.select(Task).options(
            sqlalchemy.orm.joinedload(Task.task_category),
            sqlalchemy.orm.joinedload(Task.account).joinedload(Account.wallet)
        ).where(
            Task.account_id == account_id,
            Task.is_completed == False
        )

        result = await self.async_session.execute(select_stmt)
        tasks = result.scalars().all()

        # 对每个任务进行处理，只增加那些未达到评论次数上限的任务的评论计数
        for task in tasks:
            if task.reviews_posted_since_task_start < task.task_category.reviews_posted_count:
                task.reviews_posted_since_task_start += 1
                # 检查任务是否满足完成条件
                task = await self.update_task_status(task)

        # 提交所有更改
        await self.async_session.commit()

        return tasks
    async def claim_task_reward(self, account_id:int, task_id:int) -> Task:
        stmt = sqlalchemy.select(Task).options(
            sqlalchemy.orm.joinedload(Task.task_category),
            sqlalchemy.orm.joinedload(Task.account).joinedload(Account.wallet)
        ).where(Task.account_id == account_id, Task.id == task_id)
        query = await self.async_session.execute(statement=stmt)
        task = query.scalar()
        if task.is_completed == False:
            raise HTTPException(status_code=400, detail="Task is not completed yet!")
        if task.is_claimed == True:
            raise HTTPException(status_code=400, detail="Task reward is already claimed!")
        task.is_claimed = True
        task.account.wallet.balance += task.task_category.task_reward
        await self.async_session.commit()
        await self.async_session.refresh(instance=task)
        new_query=await self.async_session.execute(
            sqlalchemy.select(Task).options(
                sqlalchemy.orm.joinedload(Task.task_category),
                sqlalchemy.orm.joinedload(Task.account).joinedload(Account.wallet)
            ).where(Task.id == task.id)
        )
        task = new_query.scalar()
        return task

    async def assign_task(self, account_id: int, task_level: int) -> Task:
        """
        为用户分配一个指定等级且之前未领取的任务。
        """
        # 查询指定等级的所有任务类别ID
        task_categories_stmt = sqlalchemy.select(TaskCategory.id).where(TaskCategory.access_level == task_level)
        task_categories_result = await self.async_session.execute(task_categories_stmt)
        task_category_ids = [category_id for category_id in task_categories_result.scalars()]

        if not task_category_ids:
            raise HTTPException(status_code=400, detail="No task categories found for the specified level.")

        # 查询用户已经领取的任务类别ID
        taken_task_categories_stmt = sqlalchemy.select(Task.task_category_id).where(
            Task.account_id == account_id,
            Task.task_category_id.in_(task_category_ids)
        )
        taken_task_categories_result = await self.async_session.execute(taken_task_categories_stmt)
        taken_task_category_ids = {taken_id for taken_id in taken_task_categories_result.scalars().all()}

        # 查找未被领取的任务类别ID
        available_category_id = next((id for id in task_category_ids if id not in taken_task_category_ids), None)
        if available_category_id is None:
            raise HTTPException(status_code=400, detail="No available tasks for the specified level.")

        # 为用户创建新的任务记录
        new_task = Task(account_id=account_id, task_category_id=available_category_id)
        self.async_session.add(new_task)
        await self.async_session.commit()
        await self.async_session.refresh(new_task)
        return new_task
    async def assign_task_by_category_id(self, account_id: int, task_category_id: int) -> Task:
        """
        为用户分配一个指定任务类别的任务。
        """
        # 查询指定任务类别
        task_category_stmt = sqlalchemy.select(TaskCategory).where(TaskCategory.id == task_category_id)
        task_category_result = await self.async_session.execute(task_category_stmt)
        task_category = task_category_result.scalar()
        if task_category is None:
            raise HTTPException(status_code=400, detail="Task category not found.")

        # 为用户创建新的任务记录
        new_task = Task(account_id=account_id, task_category_id=task_category_id)
        self.async_session.add(new_task)
        await self.async_session.commit()
        await self.async_session.refresh(new_task)
        return new_task
    def calculate_weighted_progress(self,movies_uploaded_since_task_start, reviews_posted_since_task_start,
                                    movies_uploaded_count, reviews_posted_count):
        # 初始权重
        movie_weight = 0.5
        review_weight = 0.5

        # 检查电影上传需求是否为0
        if movies_uploaded_count == 0:
            movie_progress = 100
            movie_weight = 0  # 如果没有电影上传需求，将电影的权重设为0
        else:
            movie_progress = min(100, (movies_uploaded_since_task_start / movies_uploaded_count) * 100)

        # 检查评论发布需求是否为0
        if reviews_posted_count == 0:
            review_progress = 100
            review_weight = 0  # 如果没有评论发布需求，将评论的权重设为0
        else:
            review_progress = min(100, (reviews_posted_since_task_start / reviews_posted_count) * 100)

        # 动态调整权重
        if movie_weight == 0 and review_weight == 0:
            # 如果两个权重都是0（理论上不应该发生因为至少有一个任务），避免除以0的错误
            total_weight = 1
        else:
            total_weight = movie_weight + review_weight

        # 根据可用的任务调整权重并计算总加权进度
        movie_weight /= total_weight
        review_weight /= total_weight

        # 计算总加权进度
        total_progress = movie_progress * movie_weight + review_progress * review_weight
        return total_progress

    class TaskHooks:
        def __init__(self, type, task):
            self.type = type
            self.movies_uploaded_since_task_start = task.movies_uploaded_since_task_start
            self.reviews_posted_since_task_start = task.reviews_posted_since_task_start
            self.movies_uploaded_count = task.task_category.movies_uploaded_count
            self.reviews_posted_count = task.task_category.reviews_posted_count


