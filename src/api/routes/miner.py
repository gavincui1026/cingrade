import pydantic
import fastapi

from src.api.dependencies.repository import get_repository
from src.models.schemas.miner import MinerInResponse, MinerInCreate, MinerInUpdate
from src.repository.crud.miner import MinerCRUDRepository
from src.utilities.exceptions.database import EntityDoesNotExist

router = fastapi.APIRouter(prefix="/accounts", tags=["accounts"])

@router.post(
    path="/purchase-miner",
    name="miners:purchase-miner",
    response_model=MinerInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def purchase_miner(
    miner_create: MinerInCreate,
    miner_repo: MinerCRUDRepository = fastapi.Depends(get_repository(repo_type=MinerCRUDRepository)),
) -> MinerInResponse:
    new_miner = await miner_repo.create_miner(miner=miner_create)
    return MinerInResponse(
        id=new_miner.id,
        user_id=new_miner.user_id,
        miner_config_id=new_miner.miner_config_id,
        created_at=new_miner.created_at,
        updated_at=new_miner.updated_at,
    )

@router.get(
    path="",
    name="miners:read-miners",
    response_model=list[MinerInResponse],
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_miners(
    miner_repo: MinerCRUDRepository = fastapi.Depends(get_repository(repo_type=MinerCRUDRepository)),
) -> list[MinerInResponse]:
    db_miners = await miner_repo.read_miners()
    db_miner_list: list = list()

    for db_miner in db_miners:
        miner = MinerInResponse(
            id=db_miner.id,
            user_id=db_miner.user_id,
            miner_config_id=db_miner.miner_config_id,
            created_at=db_miner.created_at,
            updated_at=db_miner.updated_at,
        )
        db_miner_list.append(miner)

    return db_miner_list



