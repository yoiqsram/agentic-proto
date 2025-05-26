from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from .asset import StockAsset


class StockAction(int, Enum):
    BUY = 1
    SELL = -1


class StockTrade(BaseModel):
    asset: StockAsset
    action: StockAction
    price: int
    commission_fee: float
    created_datetime: datetime
    execution_datetime: datetime | None = None
