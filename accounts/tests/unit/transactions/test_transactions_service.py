import pytest
from bson.objectid import ObjectId
from fastapi import HTTPException
from pymongo.collection import Collection

from schemas import CSVNames
from schemas.entities import Currency, DebitAccount
from transactions.services import _check_headers, _make_transactions, is_csv


def test_outputCorrectHeaderPositions_givenHeaderNames():
    transactions = [
        [CSVNames.AMOUNT, CSVNames.CURRENCY, CSVNames.DATE, CSVNames.DESCRIPTION]
    ]
    possitions = _check_headers(transactions=iter(transactions))
    expected = {
        CSVNames.AMOUNT: 0,
        CSVNames.CURRENCY: 1,
        CSVNames.DATE: 2,
        CSVNames.DESCRIPTION: 3,
    }
    assert possitions == expected


def test_raise_givenIncorrectHeaders():
    transactions = [
        ["Incorrect", CSVNames.CURRENCY, CSVNames.DATE, CSVNames.DESCRIPTION]
    ]
    with pytest.raises(HTTPException):
        _check_headers(transactions=iter(transactions))


def test_returnsTrue_givenCSVFile(mocker):
    file = mocker.MagicMock(filename="test.csv")
    assert is_csv(file) is True


def test_raise_givenNotCSVFile(mocker):
    file = mocker.MagicMock(filename="not_a_csv")
    with pytest.raises(HTTPException):
        is_csv(file)


@pytest.fixture
def mock_account():
    account = DebitAccount(account_currency=Currency.EUR).model_dump()
    account["_id"] = ObjectId()
    return account


def test_makeTransactions_givenAcceptableAmounts(mocker, monkeypatch, mock_account):
    class MockInsertRes:
        def __init__(self, inserted_id):
            self.inserted_id = inserted_id

    def mock_get_item(*args, **kwargs):
        return Collection

    def mock_exchange_rate(*args, **kwargs):
        return 0.5

    def mock_update(*args, **kwargs):
        return None

    def mock_insert(*args, **kwargs):
        return MockInsertRes(ObjectId())

    transactions = iter(
        [
            [
                CSVNames.AMOUNT,
                CSVNames.CURRENCY,
                CSVNames.DATE,
                CSVNames.DESCRIPTION,
            ],
            ["-1000", Currency.EUR, "2022-05-15 15:00:00", "test"],
            ["500", Currency.EUR, "2022-05-15 15:00:00", "test"],
            ["-300", Currency.EUR, "2022-05-15 15:00:00", "test"],
            ["-100", Currency.USD, "2022-05-15 15:00:00", "test"],
            ["-1000", Currency.USD, "2022-05-15 15:00:00", "test"],
            ["1000", Currency.EUR, "2022-05-15 15:00:00", "test"],
        ]
    )
    positions = _check_headers(transactions=transactions)

    client = mocker.MagicMock(__getitem__=mock_get_item)
    monkeypatch.setattr(Collection, "update_one", mock_update)
    monkeypatch.setattr(Collection, "insert_one", mock_insert)
    mocker.patch("transactions.services.get_exchange_rate", mock_exchange_rate)

    successful, failed, balance = _make_transactions(
        client=client,
        account=mock_account,
        transactions=transactions,
        possitions=positions,
    )
    assert balance == 1150
    assert len(successful) == 4
    assert len(failed) == 2
