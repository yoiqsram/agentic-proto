import pandas as pd
import time
from datetime import datetime, timedelta
from peewee import chunked
from tqdm import tqdm

from database import Stock, StockDaily, User, connect_database
from market_pipeline.stock import (
    get_stock_daily_last_date,
    get_stock_daily
)

START_DATETIME = datetime(2023, 1, 1)


def extract_stock_watchlist(username: str) -> list[Stock]:
    user = User.get(User.username == username)
    stocks = [
        watchlist.stock
        for watchlist in user.watchlist
    ]
    return stocks[:45]


def extract_stock_daily(stocks: list[Stock]) -> pd.DataFrame:
    data = []
    for stock in tqdm(stocks):
        last_date = get_stock_daily_last_date(stock.code)
        if last_date is not None:
            start_datetime = last_date + timedelta(days=1)
        else:
            start_datetime = START_DATETIME

        stock_daily = get_stock_daily(
            stock.code,
            start_datetime
        )
        stock_daily = (
            stock_daily
            .reset_index()
            .assign(stock_code=stock.code)
        )
        data.append(stock_daily)
        time.sleep(1)

    data = pd.concat(data)
    data.columns = data.columns.str.lower()
    if 'adj_close' in data.columns:
        data['close'] = 'adj_close'
    return data


def load_stock_daily_to_db(
        data: pd.DataFrame,
        *,
        chunk_size: int = 64
        ):
    data = (
        data[[
            'stock_code',
            'date',
            'open',
            'high',
            'low',
            'close',
            'volume'
        ]]
        .to_dict('records')
    )
    with db.atomic():
        for batch in chunked(data, chunk_size):
            StockDaily.insert_many(batch).execute()


if __name__ == '__main__':
    db = connect_database()

    username = 'default'
    stocks = extract_stock_watchlist(username)
    data = extract_stock_daily(stocks[:8])
    load_stock_daily_to_db(data)
