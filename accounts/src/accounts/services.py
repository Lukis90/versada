from fastapi import HTTPException, status
from pymongo import MongoClient

from schemas.entities import (
    Account,
    AccountType,
    CreateAccount,
    CreditAccount,
    DebitAccount,
)
from schemas.http import CreateAccountRequest, GetAccountBalanceRequest
from transactions import crud as tr_crud

from . import crud as ac_crud


def create_account_service(
    request: CreateAccountRequest, client: MongoClient
) -> Account:
    account = _account_factory(request)
    _id = ac_crud.create_account(
        client=client, account=CreateAccount(**account.model_dump()).model_dump()
    )
    account.id = _id
    return account


def get_accounts_service(client: MongoClient) -> list[Account]:
    docs = ac_crud.get_accounts(client=client, filter={}, projection={})
    return [Account(**doc) for doc in docs]


def get_accounts_balance(
    client: MongoClient, request: GetAccountBalanceRequest
) -> float:
    if not (
        account := ac_crud.get_account(
            client=client, filter={"_id": request.account_id}
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account does not exist."
        )
    if request.dt:
        transactions = tr_crud.get_transactions(
            client=client,
            filter={
                "account_id": str(request.account_id),
                "date": {"$lte": request.dt},
            },
        )
        return (
            sum(transaction["exchanged_amount"] for transaction in transactions),
            account["account_currency"],
        )
    return account["balance"], account["account_currency"]


def _account_factory(request):
    if request.type == AccountType.CREDIT:
        account = CreditAccount(**request.model_dump())
    elif request.type == AccountType.DEBIT:
        account = DebitAccount(**request.model_dump())
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported account type {request.type}",
        )

    return account
