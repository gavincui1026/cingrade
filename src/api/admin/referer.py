import fastapi

from src.api.dependencies.repository import get_repository
from src.api.dependencies.token import get_admin_me
from src.models.db.account import Account
from src.models.schemas.account import ReferalInResponse
from src.repository.crud.account import AccountCRUDRepository

router = fastapi.APIRouter(prefix="/referer")
@router.post(
    path="/generate-referer",
    name="referer:generate-referer",
    response_model=ReferalInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def generate_referer(
    account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
    user: Account = fastapi.Depends(get_admin_me),
):
    referer = await account_repo.create_referer(user=user)
    return ReferalInResponse(referal_code=referer.referal_code)
