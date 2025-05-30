import pandas as pd
import time
from argparse import Namespace
from datetime import datetime, timedelta
from peewee import chunked, Database
from tqdm import tqdm

from database import (
    Stock, StockDaily, Currency, CurrencyDaily,
    User,
    connect_database, enable_debug
)

from .utils.stock import (
    get_stock_daily_last_date,
    get_stock_daily
)
from .utils.currency import (
    get_currency_daily_last_date,
    get_currency_daily
)

START_DATETIME = datetime(2023, 1, 1)


def extract_stock_watchlist(username: str) -> list[Stock]:
    user = User.get(User.username == username)
    stocks = [
        watchlist.stock
        for watchlist in user.watchlist
    ]
    return stocks


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
    if 'close' not in data.columns \
            and 'adj_close' in data.columns:
        data['close'] = 'adj_close'
    return data.loc[
        lambda df: df['date'].ge(start_datetime.strftime('%Y-%m-%d'))
    ]


def load_stock_daily_to_db(
        data: pd.DataFrame,
        *,
        database: Database,
        chunk_size: int = 64,
        ):
    if len(data) == 0:
        return

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
    with database.atomic():
        for batch in chunked(data, chunk_size):
            (
                StockDaily
                .insert_many(batch)
                .on_conflict_ignore()
                .execute()
            )


def extract_currencies() -> list[Currency]:
    return list(
        Currency.select()
        .where(Currency.code != 'USD')
    )


def extract_currency_daily(currencies: list[Currency]) -> pd.DataFrame:
    data = []
    for currency in tqdm(currencies):
        last_date = get_currency_daily_last_date(
            'USD',
            currency.code
        )
        if last_date is not None:
            start_datetime = last_date + timedelta(days=1)
        else:
            start_datetime = START_DATETIME

        currency_daily = get_currency_daily(
            'USD',
            currency.code,
            start_datetime
        )
        currency_daily = (
            currency_daily
            .reset_index()
            .assign(
                from_currency_code='USD',
                to_currency_code=currency.code
            )
        )
        data.append(currency_daily)
        time.sleep(1)

    data = pd.concat(data)
    data.columns = data.columns.str.lower()
    if 'close' not in data.columns \
            and 'adj_close' in data.columns:
        data['close'] = 'adj_close'
    return data.loc[
        lambda df: df['date'].ge(start_datetime.strftime('%Y-%m-%d'))
    ]


def load_currency_daily_to_db(
        data: pd.DataFrame,
        *,
        database: Database,
        chunk_size: int = 64,
        ):
    if len(data) == 0:
        return

    data = (
        data[[
            'from_currency_code',
            'to_currency_code',
            'date',
            'open',
            'high',
            'low',
            'close'
        ]]
        .to_dict('records')
    )
    with database.atomic():
        for batch in chunked(data, chunk_size):
            (
                CurrencyDaily
                .insert_many(batch)
                .on_conflict_ignore()
                .execute()
            )


def run_daily_market_pipeline(args: Namespace):
    if args.debug:
        enable_debug()

    db = connect_database()

    username = 'default'

    stocks = extract_stock_watchlist(username)
    stock_daily = extract_stock_daily(stocks)
    load_stock_daily_to_db(stock_daily, database=db)

    currencies = extract_currencies()
    currency_daily = extract_currency_daily(currencies)
    load_currency_daily_to_db(currency_daily, database=db)
