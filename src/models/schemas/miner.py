import datetime
from src.models.schemas.base import BaseSchemaModel

class MinerInCreate(BaseSchemaModel):
    user_id: int
    miner_config_id: int

class MinerInUpdate(BaseSchemaModel):
    user_id: int
    miner_config_id: int

class MinerInResponse(BaseSchemaModel):
    id: int
    user_id: int
    miner_config_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
