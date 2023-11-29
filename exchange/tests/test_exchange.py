import pytest
from fastapi import HTTPException, status

from exchange_rates import _swap_pair, get_exchange_pairs, get_exchange_rate
from schemas import ExchangeRateResponse

PAIRS_MOCK = {"USD-EUR": 1.2}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pair, expected",
    (
        (
            "USD-EUR",
            ExchangeRateResponse(
                pair="USD-EUR", rate=1.2, status_code=status.HTTP_200_OK
            ),
        ),
        (
            "EuR-usD",
            ExchangeRateResponse(
                pair="EUR-USD", rate=0.8333, status_code=status.HTTP_200_OK
            ),
        ),
    ),
)
async def test_returnCorrectExchangeRate_givenSupportedPair(mocker, pair, expected):
    mocker.patch("exchange_rates.PAIRS", PAIRS_MOCK)
    response = await get_exchange_rate(pair=pair)
    assert response == expected


@pytest.mark.asyncio
async def test_returnStatus200_givenSupportedPair(mocker):
    mocker.patch("exchange_rates.PAIRS", PAIRS_MOCK)
    response = await get_exchange_rate(pair="EUR-USD")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_returnStatus200_returningSupportedPairs():
    response = await get_exchange_pairs()
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_raise_givenUnsupportedPair():
    with pytest.raises(HTTPException):
        await get_exchange_rate("not_supported-USD")


@pytest.mark.asyncio
async def test_returnStatus404_givenUnsupportedPair():
    with pytest.raises(HTTPException) as exception:
        await get_exchange_rate("not_supported-USD")
        assert exception.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_raise_givenOnlyOneCurrency():
    with pytest.raises(HTTPException):
        await get_exchange_rate("USD")


@pytest.mark.asyncio
async def test_returnStatus400_givenOnlyOneCurrency():
    with pytest.raises(HTTPException) as exception:
        await get_exchange_rate("USD")
        assert exception.status_code == status.HTTP_400_BAD_REQUEST


def test_correctlySwaps_givenCurrencyPair():
    expected = "EUR-USD"
    res = _swap_pair("USD-EUR")
    assert res == expected
