import datetime

import pydantic
from fastapi.security import OAuth2PasswordBearer


class JWToken(pydantic.BaseModel):
    exp: datetime.datetime
    sub: str


class JWTAccount(pydantic.BaseModel):
    username: str
    email: pydantic.EmailStr


