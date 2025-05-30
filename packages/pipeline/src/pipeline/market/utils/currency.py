import pandas as pd
import yfinance as yf
from datetime import datetime
from peewee import fn

from database import CurrencyDaily


def get_currency_daily_last_date(
        from_code: str,
        to_code: str = 'USD'
        ) -> datetime | None:
    return (
        CurrencyDaily
        .select(fn.MAX(CurrencyDaily.date).alias('date'))
        .where(
            (CurrencyDaily.from_currency_code == from_code)
            & (CurrencyDaily.to_currency_code == to_code)
        )
        .scalar()
    )


def get_currency_daily(
        from_code: str,
        to_code: str,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None
        ) -> pd.DataFrame:
    ticker = f'{from_code}{to_code}=X'
    currency_data = yf.download(
        ticker,
        start=start_datetime,
        end=end_datetime,
        group_by='ticker',
        progress=False
    )
    return currency_data.droplevel(0, axis=1)
