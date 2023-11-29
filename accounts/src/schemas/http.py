from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from . import OID, FloatTwoDecimals
from .entities import Account, AccountType, CreateTransaction, Currency, Transaction


class GetTransactionsRequest(BaseModel):
    account_id: OID


class GetTransactionsRangeRequest(GetTransactionsRequest):
    start: datetime = None
    end: datetime = None


class TransactionsResponse(BaseModel):
    transactions: list[Transaction]
    status_code: int


class CreateAccountRequest(BaseModel):
    type: AccountType
    account_currency: Currency


class CreateAccountResponse(CreateAccountRequest):
    id: OID = Field(default=None)
    debt_limit: FloatTwoDecimals
    balance: FloatTwoDecimals
    status_code: int = 200


class ImportTransactionsResponse(BaseModel):
    balance: FloatTwoDecimals
    successful: list[Transaction]
    failed: list[CreateTransaction]
    status_code: int


class GetAccountsResponse(BaseModel):
    accounts: list[Account]
    status_code: int


class GetAccountBalanceRequest(BaseModel):
    account_id: OID
    dt: Optional[datetime] = None


class GetAccountBalanceResponse(BaseModel):
    account_id: OID
    balance: FloatTwoDecimals
    currency: Currency
    status_code: int
