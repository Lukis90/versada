from fastapi import APIRouter, Depends, status
from pymongo import MongoClient

from db import get_client
from schemas.http import (
    CreateAccountRequest,
    CreateAccountResponse,
    GetAccountBalanceRequest,
    GetAccountBalanceResponse,
    GetAccountsResponse,
)

from .services import create_account_service, get_accounts_balance, get_accounts_service

router = APIRouter(prefix="/accounts", tags=["ACCOUNT"])


@router.post("/", response_model=CreateAccountResponse)
def create_account(
    request: CreateAccountRequest, client: MongoClient = Depends(get_client)
):
    account = create_account_service(client=client, request=request)
    response = CreateAccountResponse(**account.model_dump())
    response.status_code = status.HTTP_200_OK
    return response


@router.get("/", response_model=GetAccountsResponse)
def get_accounts(client: MongoClient = Depends(get_client)):
    accounts = get_accounts_service(client=client)
    status_code = status.HTTP_200_OK
    if not accounts:
        status_code = status.HTTP_204_NO_CONTENT
    return GetAccountsResponse(accounts=accounts, status_code=status_code)


@router.post("/balance", response_model=GetAccountBalanceResponse)
def get_account_balance(
    request: GetAccountBalanceRequest, client: MongoClient = Depends(get_client)
):
    balance, currency = get_accounts_balance(client=client, request=request)
    return GetAccountBalanceResponse(
        account_id=request.account_id,
        balance=balance,
        currency=currency,
        status_code=status.HTTP_200_OK,
    )
