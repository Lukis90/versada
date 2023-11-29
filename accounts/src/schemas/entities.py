from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from . import OID, FloatFourDecimals, FloatTwoDecimals


class AccountType(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class BaseTransaction(BaseModel):
    account_id: str
    date: datetime
    description: str
    amount: FloatTwoDecimals
    currency: Currency
    exchange_rate: FloatFourDecimals
    exchanged_amount: FloatTwoDecimals


class CreateTransaction(BaseTransaction):
    ...


class Transaction(BaseTransaction):
    id: OID = Field(default=None, alias="_id")


class BaseAccount(BaseModel):
    account_currency: Currency
    type: AccountType
    balance: FloatTwoDecimals = 0
    debt_limit: FloatTwoDecimals = 0


class CreateAccount(BaseAccount):
    ...


class Account(BaseAccount):
    id: OID = Field(default=None, alias="_id")


class DebitAccount(Account):
    type: AccountType = AccountType.DEBIT


class CreditAccount(Account):
    type: AccountType = AccountType.CREDIT
    debt_limit: FloatTwoDecimals = -500
