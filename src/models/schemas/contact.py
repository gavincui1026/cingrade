from typing import Optional

from src.models.schemas.base import BaseSchemaModel


class ContactInResponse(BaseSchemaModel):
    calling_code: str
    country_name: str
    country_code: str
    region_name: str
    city: str
    uuid: str

class ContactFormInCreate(BaseSchemaModel):
    phone: str
    email: str
    message: Optional[str] = None
    name: str
    uuid: str
    calling_code: str
