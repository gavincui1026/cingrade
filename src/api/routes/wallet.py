import json
from typing import List

import fastapi
from fastapi import Header

from src.api.dependencies.repository import get_repository
from src.api.dependencies.token import get_user_me
from src.config.manager import settings
from src.models.db.account import Account
from src.models.schemas.wallet import WalletInResponse, TopupInCreate, TopupInResponse, TransactionInCreate, \
    PaymentInCreate, PaymentInfo, PaymentInResponse, PaymentUpdate, TransactionInResponse, ReadTransaction, \
    WalletInUpdate, WithdrawInCreate
from src.repository.crud.wallet import WalletCrudRepository

router = fastapi.APIRouter(prefix='/wallet', tags=["wallet"])

@router.post(
    path="/top-up",
    name="wallet:create-top-up",
    response_model=PaymentInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
    description="amount使用精度为2位小数，transaction_currency可以选择usdttrc20, usdterc20, btc, eth, trx",
)
async def top_up(
    topup: TopupInCreate,
    wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)),
    user = fastapi.Depends(get_user_me),
) -> PaymentInResponse:
    try:
        paydetails = await wallet_repo.top_up(
            TransactionInCreate(
                wallet_id=user.wallet.id,
                amount=topup.amount,
                transaction_currency=topup.transaction_currency,
            )
        )
    except Exception as e:
        raise e
    print(123)
    return paydetails

@router.get(
    path="/transactions",
    name="wallet:transactions",
    response_model=WalletInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def transactions(
    user = fastapi.Depends(get_user_me),
    wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)),
) -> WalletInResponse:
    try:
        wallet = await wallet_repo.read_wallet_by_id(id=user.wallet.id)
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
    except Exception as e:
        raise e
    return WalletInResponse(
        id=wallet.id,
        account_id=wallet.account_id,
        bitcoin_address=wallet.bitcoin_address,
        usdt_address=wallet.usdt_address,
        ethereum_address=wallet.ethereum_address,
        tron_address=wallet.tron_address,
        balance=wallet.balance,
        transactions=transactions,
    )

@router.post(
    path="/ipn_callback",
    name="wallet:ipn_callback",
    status_code=fastapi.status.HTTP_200_OK,
    description="nowpayments回调接口,这个接口不要请求，是nowpayments回调接口",
)
async def ipn_callback(request: fastapi.Request,
                       wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)
                       )):
    sig=request.headers.get("x-nowpayments-sig")
    message = json.dumps(await request.json(), separators=(',', ':'), sort_keys=True)
    secret_key = settings.IPN_SECRET
    result = wallet_repo.np_signature_check(secret_key, sig, message)
    print(sig)
    if result:
        payment = await request.json()
        print(payment)
        await wallet_repo.update_payment_status(PaymentUpdate(
            payment_id=payment.get("payment_id"),
            payment_status=payment.get("payment_status"),
        ))
    else:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return {"message": "success"}

@router.post(
    path="/check_payment_status",
    name="wallet:check_payment_status",
    response_model=TransactionInResponse,
    status_code=fastapi.status.HTTP_200_OK,
    description="payment_id为支付id,轮询此接口获取支付状态",
)
async def check_payment_status(transaction: ReadTransaction,
                               wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)),
                               user=fastapi.Depends(get_user_me),
                               ) -> TransactionInResponse:
    transaction = await wallet_repo.check_payment_status(transaction)
    return TransactionInResponse(
        id=transaction.id,
        wallet_id=transaction.wallet_id,
        amount=transaction.amount,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
        transaction_type=transaction.transaction_type,
        transaction_status=transaction.transaction_status,
        transaction_currency=transaction.transaction_currency,
    )

@router.post(
    path="/update_wallet",
    name="wallet:update_wallet",
    response_model=WalletInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
    description="更新钱包地址",
)
async def update_wallet(
    addresses: WalletInUpdate,
    wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)),
    user=fastapi.Depends(get_user_me),
) -> WalletInResponse:
    wallet = await wallet_repo.read_wallet_by_account_id(account_id=user.id)
    transactions = wallet.transactions
    wallet = await wallet_repo.update_wallet(wallet, addresses)
    new_transactions = []
    for transaction in transactions:
        new_transactions.append(
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
    return WalletInResponse(
        id=wallet.id,
        account_id=wallet.account_id,
        bitcoin_address=wallet.bitcoin_address,
        usdt_address=wallet.usdt_address,
        ethereum_address=wallet.ethereum_address,
        tron_address=wallet.tron_address,
        balance=wallet.balance,
        transactions=new_transactions,
    )

@router.post(
    path="/withdraw",
    name="wallet:withdraw",
    response_model=WalletInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
    description="提现",
)
async def withdraw(
    withdraw: WithdrawInCreate,
    wallet_repo: WalletCrudRepository = fastapi.Depends(get_repository(repo_type=WalletCrudRepository)),
    user=fastapi.Depends(get_user_me),
) -> WalletInResponse:
    wallet = await wallet_repo.withdraw(withdraw, user)
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
    return WalletInResponse(
        id=wallet.id,
        account_id=wallet.account_id,
        bitcoin_address=wallet.bitcoin_address,
        usdt_address=wallet.usdt_address,
        ethereum_address=wallet.ethereum_address,
        tron_address=wallet.tron_address,
        balance=wallet.balance,
        transactions=transactions,
        )







