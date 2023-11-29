from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pymongo import MongoClient

from db import get_client
from schemas import OID
from schemas.http import (
    GetTransactionsRangeRequest,
    GetTransactionsRequest,
    ImportTransactionsResponse,
    TransactionsResponse,
)

from .services import (
    get_transactions,
    get_transactions_by_range_service,
    is_csv,
    make_transactions,
)

router = APIRouter(prefix="/transactions", tags=["TRANSACTION"])


@router.post("/import", response_model=ImportTransactionsResponse)
def import_transactions(
    file: UploadFile = File(),
    account_id: OID = Form(),
    client: MongoClient = Depends(get_client),
):
    is_csv(file)

    successful, failed, balance = make_transactions(
        client=client,
        account_id=account_id,
        file=file,
    )
    return ImportTransactionsResponse(
        balance=balance,
        successful=successful,
        failed=failed,
        status_code=status.HTTP_200_OK,
    )


@router.post("/", response_model=TransactionsResponse)
def get_all_transactions(
    request: GetTransactionsRequest, client: MongoClient = Depends(get_client)
):
    transactions = get_transactions(client=client, account_id=request.account_id)
    status_code = status.HTTP_200_OK
    if not transactions:
        status_code = status.HTTP_204_NO_CONTENT
    return TransactionsResponse(transactions=transactions, status_code=status_code)


@router.post("/range", response_model=TransactionsResponse)
def get_transactions_by_date_range(
    request: GetTransactionsRangeRequest, client: MongoClient = Depends(get_client)
):
    status_code = status.HTTP_200_OK
    transactions = get_transactions_by_range_service(client=client, request=request)
    if not transactions:
        status_code = status.HTTP_204_NO_CONTENT
    return TransactionsResponse(transactions=transactions, status_code=status_code)
