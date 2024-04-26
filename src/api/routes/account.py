import fastapi
import pydantic
from fastapi import HTTPException
from pydantic import HttpUrl

from src.api.dependencies.repository import get_repository
from src.api.dependencies.token import get_user_me
from src.models.schemas.account import AccountInResponse, AccountInUpdate, AccountWithToken
from src.models.schemas.wallet import WalletInResponse, TransactionInResponse
from src.repository.crud.account import AccountCRUDRepository
from src.repository.crud.wallet import WalletCrudRepository
from src.securities.authorizations.jwt import jwt_generator
from src.utilities.exceptions.database import EntityDoesNotExist, EntityAlreadyExists
from src.utilities.exceptions.http.exc_404 import (
    http_404_exc_email_not_found_request,
    http_404_exc_id_not_found_request,
    http_404_exc_username_not_found_request,
)

router = fastapi.APIRouter(prefix="/accounts", tags=["accounts"])


@router.get(
    path="",
    name="accountss:read-accounts",
    response_model=list[AccountInResponse],
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_accounts(
    account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
) -> list[AccountInResponse]:
    db_accounts = await account_repo.read_accounts()
    db_account_list: list = list()

    for db_account in db_accounts:
        access_token = jwt_generator.generate_access_token(account=db_account)
        account = AccountInResponse(
            id=db_account.id,
            authorized_account=AccountWithToken(
                token=access_token,
                username=db_account.username,
                email=db_account.email,  # type: ignore
                profile_picture=db_account.profile_image,
                is_verified=db_account.is_verified,
                is_active=db_account.is_active,
                is_logged_in=db_account.is_logged_in,
                created_at=db_account.created_at,
                updated_at=db_account.updated_at,
                level=db_account.level,
            ),
        )
        db_account_list.append(account)

    return db_account_list


@router.get(
    path="/{id}",
    name="accountss:read-account-by-id",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_account(
    id: int,
    account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
    wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)),
) -> AccountInResponse:
    try:
        db_account = await account_repo.read_account_by_id(id=id)
        access_token = jwt_generator.generate_access_token(account=db_account)

    except EntityDoesNotExist:
        raise await http_404_exc_id_not_found_request(id=id)

    return AccountInResponse(
        id=db_account.id,
        authorized_account=AccountWithToken(
            token=access_token,
            username=db_account.username,
            email=db_account.email,  # type: ignore
            profile_picture=db_account.profile_image,
            is_verified=db_account.is_verified,
            is_active=db_account.is_active,
            is_logged_in=db_account.is_logged_in,
            created_at=db_account.created_at,
            updated_at=db_account.updated_at,
            level=db_account.level,
        ),
        wallet=wallet_repo.read_wallet_by_id(id=db_account.id),
    )


@router.post(
    path="/update_account",
    name="accountss:update-account",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def update_account(
    user_update: AccountInUpdate,
    user=fastapi.Depends(get_user_me),
    account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
    wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)),
) -> AccountInResponse:
    query_id = user.id
    try:
        updated_db_account = await account_repo.update_account_by_id(id=query_id, account_update=user_update)

    except EntityDoesNotExist:
        raise await http_404_exc_id_not_found_request(id=query_id)

    except EntityAlreadyExists:
        raise HTTPException(status_code=409, detail="Username or email already exists")


    access_token = jwt_generator.generate_access_token(account=updated_db_account)

    return AccountInResponse(
        id=updated_db_account.id,
        authorized_account=AccountWithToken(
            token=access_token,
            username=updated_db_account.username,
            email=updated_db_account.email,  # type: ignore
            profile_picture=updated_db_account.profile_image,
            is_verified=updated_db_account.is_verified,
            is_active=updated_db_account.is_active,
            is_logged_in=updated_db_account.is_logged_in,
            created_at=updated_db_account.created_at,
            updated_at=updated_db_account.updated_at,
            level=updated_db_account.level,
        )
    )


@router.delete(path="", name="accountss:delete-account-by-id", status_code=fastapi.status.HTTP_200_OK)
async def delete_account(
    id: int, account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository))
) -> dict[str, str]:
    try:
        deletion_result = await account_repo.delete_account_by_id(id=id)

    except EntityDoesNotExist:
        raise await http_404_exc_id_not_found_request(id=id)

    return {"notification": deletion_result}

@router.get(
    path="/profile/get-profile",
    name="accountss:get-profile",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_200_OK,
    description="获取用户个人资料",
)
async def get_profile(
    user=fastapi.Depends(get_user_me),
    account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
    wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)),
) -> AccountInResponse:
    db_account = await account_repo.read_account_by_id(id=user.id)
    access_token = jwt_generator.generate_access_token(account=db_account)
    wallet = await wallet_repo.read_wallet_by_id(id=db_account.id)
    transactions = []
    for transaction in wallet.transactions:
        transactions.append(
            TransactionInResponse(
                id=transaction.id,
                wallet_id=transaction.wallet_id,
                amount=transaction.amount,
                created_at=transaction.created_at,
                updated_at=transaction.updated_at,
                transaction_type=transaction.transaction_type,
                transaction_status=transaction.transaction_status,
                transaction_currency=transaction.transaction_currency,
            )
        )
    return AccountInResponse(
        id=db_account.id,
        authorized_account=AccountWithToken(
            token=access_token,
            username=db_account.username,
            email=db_account.email,  # type: ignore
            profile_picture=db_account.profile_image,
            is_verified=db_account.is_verified,
            is_active=db_account.is_active,
            is_logged_in=db_account.is_logged_in,
            created_at=db_account.created_at,
            updated_at=db_account.updated_at,
            level=db_account.level,
        ),
        wallet=WalletInResponse(
            id=wallet.id,
            account_id=wallet.account_id,
            bitcoin_address=wallet.bitcoin_address,
            usdt_address=wallet.usdt_address,
            ethereum_address=wallet.ethereum_address,
            tron_address=wallet.tron_address,
            balance=wallet.balance,
            transactions=transactions,
            )
        )

@router.get(
    path="/customer_service/whatsapp",
    name="accountss:get-customer-service",
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_customer_service(
        account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
):

    whatsapp_url = await account_repo.read_customer_service()
    return {"whatsapp_url": whatsapp_url.whatsapp}







