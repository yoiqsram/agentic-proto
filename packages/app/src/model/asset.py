from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class Currency(str, Enum):
    IDR = 'IDR'


class StockOHLCV(BaseModel):
    code: str
    open: int
    high: int
    low: int
    close: int
    volume: int


class StockAsset(BaseModel):
    code: str
    amount: int


class CashBalance(BaseModel):
    username: str
    currency: Currency = Currency.IDR
    balance_before: float
    balance_after: float
    balance_datetime: datetime


class StockBalance(BaseModel):
    username: str
    assets: list[StockAsset]
