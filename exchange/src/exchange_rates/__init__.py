from fastapi import APIRouter, HTTPException, status

from schemas import CurrencyPairResponse, ExchangeRateResponse

PAIRS = {"EUR-USD": 1.09, "EUR-GBP": 0.87, "USD-GBP": 0.81}

router = APIRouter(prefix="/exchange")


def _swap_pair(pair: str) -> str:
    cur1, cur2 = pair.split("-")
    return f"{cur2}-{cur1}"


@router.get("/rates/{pair}")
async def get_exchange_rate(pair: str) -> ExchangeRateResponse:
    if "-" not in pair:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Malformed curency pair {pair}",
        )
    pair = pair.upper()
    if PAIRS.get(pair):
        rate = round(PAIRS[pair], 4)
    else:
        swapped_pair = _swap_pair(pair=pair)
        if PAIRS.get(swapped_pair):
            rate = round(1 / PAIRS[swapped_pair], 4)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unsuported curency pair {pair}",
            )

    return ExchangeRateResponse(pair=pair, rate=rate, status_code=200)


@router.get("/pairs")
async def get_exchange_pairs() -> CurrencyPairResponse:
    return CurrencyPairResponse(pairs=PAIRS.keys(), status_code=status.HTTP_200_OK)
