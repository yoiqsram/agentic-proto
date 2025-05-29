import pandas as pd
import yfinance as yf
from datetime import datetime
from peewee import fn

from database import StockDaily


def get_stock_daily_last_date(
        stock_code: str
        ) -> datetime | None:
    query = (
        StockDaily
        .select(fn.MAX(StockDaily.date).alias('date'))
        .where(StockDaily.stock_code == stock_code)
    )
    for record in query:
        return record.date


def get_stock_daily(
        stock_code: str,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None
        ) -> pd.DataFrame: 
    stock_data = yf.download(
        stock_code,
        start=start_datetime,
        end=end_datetime,
        group_by='ticker',
        progress=False
    )
    return stock_data.droplevel(0, axis=1)
