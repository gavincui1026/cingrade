import fastapi

from src.api.dependencies.repository import get_repository
from src.models.schemas.contact import ContactFormInCreate
from src.repository.crud.contact import ContactCRUDRepository

router = fastapi.APIRouter(prefix="/contacts", tags=["contacts"])

@router.get(
    path="",
    name="contacts:read-contacts",
    status_code=fastapi.status.HTTP_200_OK,
    description="获取用户信息，uuid存储起来，在提交表单时一并提交",
)
async def get_user_info(
        request: fastapi.Request,
        contact_repo: ContactCRUDRepository = fastapi.Depends(get_repository(repo_type=ContactCRUDRepository)),
):
    contact = await contact_repo.get_user_info(request=request)
    return contact

@router.post(
    path="/submit",
    name="contacts:create-contact",
    status_code=fastapi.status.HTTP_201_CREATED,
    description="提交表单，message设置为选填",
)
async def create_contact(
        request: fastapi.Request,
        form: ContactFormInCreate,
        contact_repo: ContactCRUDRepository = fastapi.Depends(get_repository(repo_type=ContactCRUDRepository)),
):
    contact = await contact_repo.create_contact(form=form)
    return {"message": "Contact form submitted successfully!"}