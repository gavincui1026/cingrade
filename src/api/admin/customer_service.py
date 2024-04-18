import fastapi
from pydantic import HttpUrl

from src.api.dependencies.repository import get_repository
from src.repository.crud.account import AccountCRUDRepository

router = fastapi.APIRouter()
@router.get(
    path="/update_customer_service/whatsapp/{whatsapp_url}",
    name="accountss:update-customer-service",
    status_code=fastapi.status.HTTP_200_OK,
)
async def update_customer_service(
        whatsapp_url: HttpUrl,
        account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
) :

    updated_whatsapp_url = await account_repo.update_customer_service(whatsapp_url=whatsapp_url)
    return {"whatsapp_url": whatsapp_url.whatsapp}