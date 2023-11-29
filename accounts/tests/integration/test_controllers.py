from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from db import get_client
from main import app
from schemas.entities import AccountType, Currency
from schemas.http import CreateAccountRequest


def override_get_client():
    try:
        client = MongoClient()
        db = client["test"]
        yield db
    finally:
        client.close()


def drop_db():
    client = MongoClient()
    client.drop_database("test")
    client.close()


app.dependency_overrides[get_client] = override_get_client
client = TestClient(app=app)


def test_calculatesBalanceCorrectly_givenTransactionList():
    create_request = CreateAccountRequest(
        type=AccountType.CREDIT, account_currency=Currency.USD
    )
    res = client.post("/accounts/", json=create_request.model_dump()).json()

    file_path = Path.cwd() / "../data_for_import_test/transaction_positive.csv"
    with open(file_path, "rb") as f:
        response = client.post(
            "/transactions/import", data={"account_id": res["id"]}, files={"file": f}
        ).json()
    assert response["balance"] == 345
    drop_db()


def test_balanceGoesNegativeForCreditAccount_givenTransactionList():
    create_request = CreateAccountRequest(
        type=AccountType.CREDIT, account_currency=Currency.USD
    )
    res = client.post("/accounts/", json=create_request.model_dump()).json()

    file_path = Path.cwd() / "../data_for_import_test/transaction_negative.csv"
    with open(file_path, "rb") as f:
        response = client.post(
            "/transactions/import", data={"account_id": res["id"]}, files={"file": f}
        ).json()
    assert response["balance"] == -282
    drop_db()


@pytest.mark.parametrize(
    "end, expected_balance",
    (
        (datetime(2022, 8, 14), 100),
        (datetime(2022, 6, 14), 300),
        (datetime(2022, 5, 13), 500),
    ),
)
def test_balanceGoesNegativeForCreditAccount_givenTransactionList(
    end, expected_balance
):
    create_request = CreateAccountRequest(
        type=AccountType.CREDIT, account_currency=Currency.EUR
    )
    res = client.post("/accounts/", json=create_request.model_dump()).json()

    file_path = Path.cwd() / "../data_for_import_test/transaction_range.csv"
    with open(file_path, "rb") as f:
        client.post(
            "/transactions/import", data={"account_id": res["id"]}, files={"file": f}
        )

    response = client.post(
        "/accounts/balance",
        json={"account_id": res["id"], "dt": str(end)},
    ).json()
    assert response["balance"] == expected_balance
    drop_db()
