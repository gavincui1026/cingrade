import datetime
from typing import Optional

import pydantic
from pydantic import HttpUrl

from src.models.schemas.base import BaseSchemaModel
from src.models.schemas.wallet import WalletInResponse


class AccountInCreate(BaseSchemaModel):
    username: str
    email: pydantic.EmailStr
    password: str
    referral_code: str


class AccountInUpdate(BaseSchemaModel):
    username: Optional[str] = None
    email: Optional[pydantic.EmailStr] = None
    password: Optional[str] = None
    profile_image: Optional[HttpUrl] = None


class AccountInLogin(BaseSchemaModel):
    # username: Optional[str] = None
    # email: Optional[pydantic.EmailStr] = None
    # 一个字段
    username_or_email: str
    password: str


class AccountWithToken(BaseSchemaModel):
    profile_picture: str
    token: str
    username: str
    email: pydantic.EmailStr
    is_verified: bool
    is_active: bool
    is_logged_in: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    level: int

class IPCheckInResponse(BaseSchemaModel):
    ip: str
    is_proxy: bool
    ip_location: str

class AccountInResponse(BaseSchemaModel):
    id: int
    authorized_account: AccountWithToken
    wallet: Optional[WalletInResponse]=None

class ReferalInResponse(BaseSchemaModel):
    referal_code: str
