import fastapi

from src.api.dependencies.repository import get_repository
from src.models.schemas.wallet import WalletInAdd
from src.repository.crud.wallet import WalletCrudRepository

router = fastapi.APIRouter(prefix="/wallet")





@router.post(
    path="/add_balance",
    name="wallet:add-balance",
    status_code=fastapi.status.HTTP_200_OK,
    description="添加余额"
)
async def add_balance(
    wallet: WalletInAdd,
    wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)),
) -> fastapi.Response:
    new_wallet = await wallet_repo.add_balance(wallet=wallet)
    return fastapi.Response(status_code=fastapi.status.HTTP_200_OK, content=f"Balance added to account {wallet.account_id}")