from typing import Annotated

import fastapi
from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from src.api.dependencies.repository import get_repository
from src.models.db.account import Account
from src.repository.crud.account import AccountCRUDRepository
from src.securities.authorizations.jwt import jwt_generator
import jwt

from src.utilities.exceptions.http.exc_401 import http_exc_401_cunauthorized_request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user_me(
        request: fastapi.Request,
        token: str = Header(...),
        account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
) -> Account:
    try:
        username = jwt_generator.retrieve_details_from_token(token=token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


    db_account = await account_repo.read_account_by_username(username=username, request=request)

    if db_account is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_account

async def get_admin_me(
        token: str = Header(...),
        account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
) -> Account:
    try:
        username = jwt_generator.retrieve_details_from_token(token=token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    db_account = await account_repo.read_admin_account(username=username)

    if db_account is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_account