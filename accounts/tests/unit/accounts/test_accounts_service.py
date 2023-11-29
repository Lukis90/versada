import pytest
from pydantic import ValidationError

from accounts.services import _account_factory
from schemas import CSVNames
from schemas.entities import AccountType, CreditAccount, Currency, DebitAccount
from schemas.http import CreateAccountRequest


@pytest.mark.parametrize(
    "create_request, expected",
    (
        (
            CreateAccountRequest(
                account_currency=Currency.USD, type=AccountType.CREDIT
            ),
            CreditAccount(account_currency=Currency.USD),
        ),
        (
            CreateAccountRequest(account_currency=Currency.USD, type=AccountType.DEBIT),
            DebitAccount(account_currency=Currency.USD),
        ),
    ),
)
def test_createExpectedAccount_givenAccountType(create_request, expected):
    account = _account_factory(request=create_request)
    assert account == expected


def test_raise_givenUnsupportedAccountType():
    with pytest.raises(ValidationError):
        CreateAccountRequest(account_currency=Currency.USD, type="Unsupported")


def test_outputCorrectHeaderPositions_givenHeaderNames():
    headers = [CSVNames.AMOUNT, CSVNames.CURRENCY, CSVNames.DATE, CSVNames.DESCRIPTION]
