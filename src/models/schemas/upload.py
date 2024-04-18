import datetime

from src.models.schemas.base import BaseSchemaModel
from pydantic import field_validator, HttpUrl


class UploadCreate(BaseSchemaModel):
    md5: str
    ext: str
    @field_validator('ext')
    def is_valid_ext(cls, value):
        # 只允许上传图片和视频
        supported_ext = ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi', 'mkv']
        if value not in supported_ext:
            raise ValueError(f"File extension `{value}` is not supported! Supported extensions are: {supported_ext}")
        return value


class UploadResponse(BaseSchemaModel):
    url: HttpUrl
    fields: dict