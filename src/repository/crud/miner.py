import typing

import sqlalchemy
from sqlalchemy.sql import functions as sqlalchemy_functions

from src.models.db.miner import Miner, MinerConfig
from src.models.schemas.miner import MinerInCreate
from src.repository.crud.base import BaseCRUDRepository
from src.utilities.exceptions.database import EntityAlreadyExists, EntityDoesNotExist

class MinerCRUDRepository(BaseCRUDRepository):
    async def create_miner(self, miner: MinerInCreate) -> Miner:
        new_miner = Miner(user_id=miner.user_id, config_id=miner.miner_config_id)
        self.async_session.add(instance=new_miner)
        await self.async_session.commit()
        await self.async_session.refresh(instance=new_miner)
        return new_miner



    async def read_miners(self) -> typing.Sequence[Miner]:
        stmt = sqlalchemy.select(Miner)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()

    async def read_miner_by_id(self, id: int) -> Miner:
        stmt = sqlalchemy.select(Miner).where(Miner.id == id)
        query = await self.async_session.execute(statement=stmt)

        if not query:
            raise EntityDoesNotExist(f"Miner with id `{id}` does not exist!")

        return query.scalar()  # type: ignore

    async def read_miner_by_user_id(self, user_id: int) -> Miner:
        stmt = sqlalchemy.select(Miner).where(Miner.user_id == user_id)
        query = await self.async_session.execute(statement=stmt)

        if not query:
            raise EntityDoesNotExist(f"Miner with user id `{user_id}` does not exist!")

        return query.scalar()  # type: ignore