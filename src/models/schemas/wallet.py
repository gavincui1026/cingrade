import datetime
import re
from typing import Optional

from pydantic import field_validator
from typing_extensions import Annotated
from src.utilities.formatters.crypto import is_valid_tron_address, is_valid_ethereum_address, is_valid_bitcoin_address

from src.models.schemas.base import BaseSchemaModel

class WalletInCreate(BaseSchemaModel):
    account_id: int
    balance: float = 0.0

class WalletInUpdate(BaseSchemaModel):
    bitcoin_address: Optional[str] = None
    usdt_address: Optional[str] = None
    ethereum_address: Optional[str] = None
    tron_address: Optional[str] = None

    @field_validator('bitcoin_address')
    def is_valid_bitcoin_address(cls, value):
        if value is not None:
            assert is_valid_bitcoin_address(value)
        return value
    @field_validator('usdt_address')
    def is_valid_usdt_address(cls, value):
        if value is not None:
            assert is_valid_tron_address(value)
        return value
    @field_validator('ethereum_address')
    def is_valid_ethereum_address(cls, value):
        if value is not None:
            assert is_valid_ethereum_address(value)
        return value
    @field_validator('tron_address')
    def is_valid_tron_address(cls, value):
        if value is not None:
            assert is_valid_tron_address(value)
        return value



class TransactionInCreate(BaseSchemaModel):
    wallet_id: int
    amount: float
    transaction_currency: str
    @field_validator('transaction_currency')
    def is_valid_transaction_currency(cls, value):
        supported_currencies = ['usdttrc20', 'btc', 'eth', 'usdterc20']
        if value not in supported_currencies:
            raise ValueError(f"Transaction currency `{value}` is not supported! Supported currencies are: {supported_currencies}")
        return value

class TransactionInResponse(BaseSchemaModel):
    id: int
    wallet_id: int
    amount: float
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    transaction_type: str
    transaction_status: str
    transaction_currency: str

class WalletInResponse(BaseSchemaModel):
    id: int
    account_id: int
    bitcoin_address: Optional[str]=None
    usdt_address: Optional[str]=None
    ethereum_address: Optional[str]=None
    tron_address: Optional[str]=None
    balance: float
    transactions: Optional[list[TransactionInResponse]] = None

class TopupInCreate(BaseSchemaModel):
    amount: float
    transaction_currency: str
class PaymentInCreate(BaseSchemaModel):
    price_amount: float
    pay_currency: str
    order_id: str
class TopupInResponse(BaseSchemaModel):
    transaction: TransactionInResponse
    payment: PaymentInCreate

class PaymentInfo(BaseSchemaModel):
    payment_id: int
    payment_status: str
    pay_address: str
    price_amount: float
    price_currency: str
    pay_amount: float
    actually_paid: float
    pay_currency: str
    order_id: str
    order_description: str
    purchase_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    outcome_amount: float
    outcome_currency: str

class PaymentInResponse(BaseSchemaModel):
    payment_id: int
    pay_address: str
    price_amount: float
    price_currency: str
    pay_amount: float
    pay_currency: str
    created_at: datetime.datetime
    expiration_estimate_date: datetime.datetime
    payment_status: str

class PaymentUpdate(BaseSchemaModel):
    payment_id: int
    payment_status: str

class ReadTransaction(BaseSchemaModel):
    payment_id: int | None

class WithdrawInCreate(BaseSchemaModel):
    amount: float
    withdrawal_method: str

class WalletInAdd(BaseSchemaModel):
    account_id: int
    amount: float

