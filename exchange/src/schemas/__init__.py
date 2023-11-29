from typing import Iterable

from pydantic import BaseModel


class ExchangeRateResponse(BaseModel):
    pair: str
    status_code: int
    rate: float


class CurrencyPairResponse(BaseModel):
    pairs: Iterable[str]
    status_code: int
