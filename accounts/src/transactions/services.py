import csv
from io import StringIO
from typing import Iterable, Optional

import requests
from bson.objectid import ObjectId
from fastapi import HTTPException, UploadFile, status
from pymongo import MongoClient

from accounts import crud as ac_crud
from config import EXCHANGE_URL
from schemas import OID, CSVNames
from schemas.entities import CreateTransaction, Transaction
from schemas.http import GetTransactionsRangeRequest
from transactions import crud as tr_crud


def make_transactions(
    client: MongoClient, account_id: OID, file: UploadFile
) -> tuple[list[Transaction], list[Transaction]]:
    if not (
        account := ac_crud.get_account(
            client=client,
            filter={"_id": account_id},
            projection={"_id": 1, "balance": 1, "debt_limit": 1, "account_currency": 1},
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account does not exist."
        )

    content = file.file.read()
    transactions = csv.reader(StringIO(content.decode()))
    file.file.close()
    possitions = _check_headers(transactions)

    successful, failed, current_balance = _make_transactions(
        client,
        account,
        transactions,
        possitions,
    )
    ac_crud.update_balance(
        client=client, account_id=account["_id"], balance=current_balance
    )
    return successful, failed, current_balance


def get_transactions(client: MongoClient, account_id: OID) -> list[Transaction]:
    if not (
        ac_crud.get_account(
            client=client,
            filter={"_id": account_id},
            projection={"_id": 1},
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account does not exist."
        )
    transactions = tr_crud.get_transactions(
        client=client, filter={"account_id": str(account_id)}
    )
    return [Transaction(**doc) for doc in transactions]


def get_transactions_by_range_service(
    client: MongoClient, request: GetTransactionsRangeRequest
) -> list[Transaction]:
    if not ac_crud.get_account(
        client=client,
        filter={"_id": request.account_id},
        projection={"_id": 1},
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account does not exist."
        )
    transactions = tr_crud.get_transactions(
        client=client,
        filter={
            "account_id": str(request.account_id),
            "date": {"$gte": request.start, "$lte": request.end},
        },
    )
    return [Transaction(**doc) for doc in transactions]


def get_exchange_rate(pair: str) -> float:
    res = requests.get(EXCHANGE_URL.format(pair=pair)).json()
    if "rate" not in res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=res["detail"])
    return float(res["rate"])


def is_csv(file) -> Optional[bool]:
    if file.filename.split(".")[-1].lower() != "csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At the moment we only support CSV files.",
        )
    return True


def _check_headers(transactions: list[list[str]]) -> dict:
    headers = next(transactions, None)
    headers = [header.lower() for header in headers]
    if not all(name in headers for name in CSVNames.to_list()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV file headers have to contain these values: {CSVNames.to_list()}."
            "Please check your CSV file headers.",
        )
    return {
        CSVNames.DATE: headers.index(CSVNames.DATE),
        CSVNames.DESCRIPTION: headers.index(CSVNames.DESCRIPTION),
        CSVNames.AMOUNT: headers.index(CSVNames.AMOUNT),
        CSVNames.CURRENCY: headers.index(CSVNames.CURRENCY),
    }


def _make_transactions(
    client: MongoClient,
    account: dict,
    transactions: Iterable[list[str]],
    possitions: dict,
) -> tuple[list[Transaction], list[CreateTransaction], float]:
    current_balance = account["balance"]
    debt_limit = account["debt_limit"]
    account_currency = account["account_currency"]

    successful = []
    failed = []
    for row in transactions:
        amount = float(row[possitions[CSVNames.AMOUNT]])
        rate = 1
        if row[possitions[CSVNames.CURRENCY]] != account_currency:
            pair = f"{row[possitions[CSVNames.CURRENCY]]}-{account_currency}"
            rate = get_exchange_rate(pair)
        exchanged_amount = round(amount * rate, 2)
        transaction = _form_transaction(
            possitions=possitions, row=row, amount=amount, rate=rate, _id=account["_id"]
        )
        if current_balance + exchanged_amount >= debt_limit:
            current_balance += exchanged_amount
            _id = tr_crud.insert_transaction(
                client=client, transaction=transaction.model_dump()
            )
            transaction = Transaction(**transaction.model_dump())
            transaction.id = _id
            successful.append(transaction)
        else:
            failed.append(transaction)
    return successful, failed, current_balance


def _form_transaction(
    possitions: dict, row: list[str], amount: float, rate: float, _id: ObjectId
) -> CreateTransaction:
    return CreateTransaction(
        date=row[possitions[CSVNames.DATE]],
        account_id=str(_id),
        description=row[possitions[CSVNames.DESCRIPTION]],
        amount=amount,
        currency=row[possitions[CSVNames.CURRENCY]],
        exchange_rate=rate,
        exchanged_amount=amount * rate,
    )
