import pandas as pd
from datetime import datetime

from database import connect_database, Stock, StockDaily


def get_stock_daily_data(
        stock_code: str,
        start_date: datetime,
        end_date: datetime | None = None
        )-> pd.DataFrame:
    if Stock._meta.database is None:
        connect_database()

    if end_date is None:
        end_date = datetime.now()

    stock = Stock.select().where(Stock.code == stock_code).get()

    data = pd.DataFrame(
        StockDaily
        .select()
        .where(
            (StockDaily.stock == stock)
            & (StockDaily.date >= start_date)
            & (StockDaily.date <= end_date)
        )
        .order_by(StockDaily.date)
        .dicts()
    )
    data = (
        data
        .assign(date=lambda df: pd.to_datetime(df['date']))
        .set_index(data['date'])
        [['date', 'open', 'high', 'low', 'close', 'volume']]
    )
    return data
