import fastapi

from src.api.dependencies.repository import get_repository
from src.models.schemas.account import AccountInCreate, AccountInLogin, AccountInResponse, AccountWithToken
from src.models.schemas.wallet import WalletInCreate, WalletInResponse, TransactionInResponse
from src.repository.crud.account import AccountCRUDRepository
from src.repository.crud.task import TaskCrudRepository
from src.repository.crud.wallet import WalletCrudRepository
from src.securities.authorizations.jwt import jwt_generator
from src.utilities.exceptions.database import EntityAlreadyExists
from src.utilities.exceptions.http.exc_400 import (
    http_exc_400_credentials_bad_signin_request,
    http_exc_400_credentials_bad_signup_request,
)

router = fastapi.APIRouter(prefix="/auth", tags=["authentication"])





@router.post(
    "/signup",
    name="auth:signup",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def signup(
    request: fastapi.Request,
    account_create: AccountInCreate,
    account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
) -> AccountInResponse:
    try:
        # await account_repo.verify_recapcha(recaptcha=recaptcha)
        await account_repo.is_username_taken(username=account_create.username)
        await account_repo.is_email_taken(email=account_create.email)
        await account_repo.is_referral_code_valid(referral_code=account_create.referral_code)

    except Exception as e:
        print(e)
        raise await http_exc_400_credentials_bad_signup_request()
    new_account, wallet = await account_repo.create_account(account_create=account_create,request=request)
    access_token = jwt_generator.generate_access_token(account=new_account)
    # tasks= await account_repo.apply_default_tasks(account_id=account.id)
    return AccountInResponse(
        id=new_account.id,
        authorized_account=AccountWithToken(
            token=access_token,
            username=new_account.username,
            email=new_account.email,  # type: ignore
            profile_picture=new_account.profile_image,
            is_verified=new_account.is_verified,
            is_active=new_account.is_active,
            is_logged_in=new_account.is_logged_in,
            created_at=new_account.created_at,
            updated_at=new_account.updated_at,
            level=new_account.level,
        ),
        wallet=WalletInResponse(
            id=wallet.id,
            account_id=wallet.account_id,
            bitcoin_address=wallet.bitcoin_address,
            usdt_address=wallet.usdt_address,
            ethereum_address=wallet.ethereum_address,
            tron_address=wallet.tron_address,
            balance=wallet.balance,
            transactions=[]
        )
    )


@router.post(
    path="/signin",
    name="auth:signin",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_202_ACCEPTED,
)
async def signin(
    request: fastapi.Request,
    account_login: AccountInLogin,
    account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
    wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)),
) -> AccountInResponse:
    db_account = await account_repo.read_user_by_password_authentication(account_login=account_login, request=request)
    access_token = jwt_generator.generate_access_token(account=db_account)
    wallet= await wallet_repo.read_wallet_by_account_id(account_id=db_account.id)
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
            transactions=transactions
        )
    )

