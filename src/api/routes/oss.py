import logging
import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies.repository import get_repository
from src.api.dependencies.token import get_user_me

from src.models.schemas.upload import UploadCreate, UploadResponse
from src.repository.crud.upload import UploadRepository

router = APIRouter(prefix="/oss", tags=["oss"])

@router.post(
    "/get_oss_presigned_post",
    name="获取oss上传地址",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def get_oss_presigned_post(
    upload: UploadCreate,
    upload_repo: UploadRepository = Depends(get_repository(repo_type=UploadRepository)),
    user=Depends(get_user_me),
) -> UploadResponse:
    upload_response = await upload_repo.create_presigned_post(upload=upload, user_id=user.id)
    return UploadResponse(
        url=upload_response.get("url"),
        fields=upload_response.get("fields"),
    )
