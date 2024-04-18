import hashlib
import hmac
import json
import random
import time
import typing

import requests
import sqlalchemy
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from src.models.db.account import Account
from src.models.db.wallet import Wallet, Transactions
from src.models.schemas.wallet import WalletInCreate, TransactionInCreate, WalletInResponse, TransactionInResponse, \
    TopupInResponse, PaymentInCreate, PaymentInResponse, PaymentInfo, PaymentUpdate, WalletInUpdate, WithdrawInCreate, \
    WalletInAdd
from src.repository.crud.base import BaseCRUDRepository
from src.config.manager import settings
class WalletCrudRepository(BaseCRUDRepository):
    async def create_wallet(self, wallet_create: WalletInCreate) -> Wallet:
        new_wallet = Wallet(account_id=wallet_create.account_id, balance=wallet_create.balance)
        self.async_session.add(instance=new_wallet)
        await self.async_session.commit()
        await self.async_session.refresh(instance=new_wallet)

        return new_wallet

    async def read_wallets(self) -> typing.Sequence[Wallet]:
        stmt = sqlalchemy.select(Wallet)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()

    async def read_wallet_by_id(self, id: int) -> Wallet:
        stmt = sqlalchemy.select(Wallet).options(sqlalchemy.orm.joinedload(Wallet.transactions)).where(Wallet.id == id)
        result = await self.async_session.execute(stmt)
        wallet = result.scalars().first()
        return wallet
    async def read_wallet_by_account_id(self, account_id: int) -> Wallet:
        stmt = sqlalchemy.select(Wallet).options(sqlalchemy.orm.joinedload(Wallet.transactions)).where(Wallet.account_id == account_id)
        query = await self.async_session.execute(statement=stmt)
        return query.scalar()

    async def top_up(self, transaction: TransactionInCreate):
        wallet = await self.read_wallet_by_id(id=transaction.wallet_id)
        order_id = self.generate_transaction_id(user_id=transaction.wallet_id)
        payment = await self.create_payment(PaymentInCreate(
            price_amount=transaction.amount,
            order_id=order_id,
            pay_currency=transaction.transaction_currency
        ))
        new_transaction = Transactions(wallet_id=transaction.wallet_id,
                                       amount=transaction.amount,
                                       transaction_type='top-up',
                                       transaction_currency=transaction.transaction_currency,
                                       transaction_status='pending',
                                       order_id=order_id,
                                       payment_id=payment['payment_id'],
        )
        wallet.transactions.append(new_transaction)
        self.async_session.add(instance=wallet)
        await self.async_session.commit()
        await self.async_session.refresh(instance=wallet)
        payment=PaymentInResponse(
            payment_id=payment['payment_id'],
            pay_address=payment['pay_address'],
            price_amount=payment['price_amount'],
            price_currency=payment['price_currency'],
            pay_amount=payment['pay_amount'],
            pay_currency=payment['pay_currency'],
            created_at=payment['created_at'],
            expiration_estimate_date=payment['expiration_estimate_date'],
            payment_status=payment['payment_status'],
        )
        return payment

    async def withdraw(self, withdraw: WithdrawInCreate, user: Account):
        wallet = await self.read_wallet_by_id(id=user.wallet.id)
        if withdraw.amount > wallet.balance:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        wallet.balance -= withdraw.amount
        transaction = Transactions(
            wallet_id=user.wallet.id,
            amount=withdraw.amount,
            transaction_type='withdraw',
            transaction_currency=withdraw.withdrawal_method,
            transaction_status='pending',
            order_id=self.generate_transaction_id(user_id=user.wallet.id),
        )
        wallet.transactions.append(transaction)
        await self.async_session.commit()
        await self.async_session.refresh(instance=wallet)
        wallet = await self.read_wallet_by_id(id=wallet.id)
        return wallet



    async def read_transactions(self) -> typing.Sequence[Transactions]:
        stmt = sqlalchemy.select(Transactions)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()

    async def read_transaction_by_user_id(self, wallet_id: int) -> Transactions:
        stmt = sqlalchemy.select(Transactions).where(Transactions.wallet_id == wallet_id)
        query = await self.async_session.execute(statement=stmt)
        return query.scalar()

    def generate_transaction_id(self, user_id):
        unique_string = f"{user_id}-{int(time.time())}-{random.randint(0, 1e6)}"
        transaction_id = hashlib.sha256(unique_string.encode()).hexdigest()
        return transaction_id

    def np_signature_check(self,np_secret_key, np_x_signature, message):
        sorted_msg = message
        digest = hmac.new(
            str(np_secret_key).encode(),
            f'{sorted_msg}'.encode(),
            hashlib.sha512)
        signature = digest.hexdigest()
        print(signature)
        print(np_x_signature)
        if signature == np_x_signature:
            return True
        else:
            raise Exception("Signature check failed")

    async def create_payment(self, payment: PaymentInCreate) -> Transactions:
        url = "https://api.nowpayments.io/v1/payment"
        headers = {
            "x-api-key": settings.NOWPAYMENTS_API_KEY,
        }
        data = {
          "price_amount": payment.price_amount,
          "price_currency": "usd",
          "pay_currency": payment.pay_currency,
          "ipn_callback_url": f"{settings.EXTERNAL_REQUEST_URL}/api/wallet/ipn_callback",
          "order_id": payment.order_id,
          "order_description": "Acount top-up",
        }
        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()
        return response_data

    async def update_payment_status(self, payment: PaymentUpdate):
        # update payment status并更新钱包余额
        stmt = sqlalchemy.select(Transactions).options(selectinload(Transactions.wallet)).where(Transactions.payment_id == payment.payment_id)
        query = await self.async_session.execute(statement=stmt)
        transaction = query.scalar()
        transaction.transaction_status = payment.payment_status
        if payment.payment_status == 'finished':
            transaction.wallet.balance += transaction.amount
        self.async_session.add(instance=transaction)
        await self.async_session.commit()
        await self.async_session.refresh(instance=transaction)
        return transaction

    async def check_payment_status(self, transaction) -> Transactions:
        stmt = sqlalchemy.select(Transactions).where(Transactions.payment_id == transaction.payment_id)
        query = await self.async_session.execute(statement=stmt)
        transaction = query.scalar()
        return transaction

    async def update_wallet(self, wallet: Wallet,addresses:WalletInUpdate) -> Wallet:
        wallet.bitcoin_address=addresses.bitcoin_address
        wallet.usdt_address=addresses.usdt_address
        wallet.ethereum_address=addresses.ethereum_address
        wallet.tron_address=addresses.tron_address
        self.async_session.add(instance=wallet)
        await self.async_session.commit()
        await self.async_session.refresh(instance=wallet)
        stmt = sqlalchemy.select(Wallet).options(sqlalchemy.orm.joinedload(Wallet.transactions)).where(Wallet.id == wallet.id)
        result = await self.async_session.execute(stmt)
        wallet = result.scalars().first()
        return wallet

    async def session_update(self, wallet: Wallet) -> Wallet:
        self.async_session.add(instance=wallet)
        await self.async_session.commit()
        await self.async_session.refresh(instance=wallet)
        return wallet

    async def add_balance(self, wallet: WalletInAdd) -> Wallet:
        wallet = await self.read_wallet_by_account_id(account_id=wallet.account_id)
        wallet.balance += wallet.balance
        self.async_session.add(instance=wallet)
        await self.async_session.commit()
        await self.async_session.refresh(instance=wallet)
        return wallet








