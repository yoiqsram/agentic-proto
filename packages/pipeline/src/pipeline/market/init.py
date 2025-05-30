import pandas as pd
import requests
from argparse import Namespace
from lxml import html
from pathlib import Path
from peewee import Database, chunked, fn

from database import (
    Sector, Stock, User, UserStockWatchlist,
    Currency, CurrencyDaily,
    connect_database, enable_debug
)

SECTOR_MAP = {
    'Basic Materials': 'IDXBASIC',
    'Consumer Cyclicals': 'IDXCYCLIC',
    'Consumer Non-Cyclicals': 'IDXNONCYCLIC',
    'Energy': 'IDXENERGY',
    'Financials': 'IDXFINANCE',
    'Healthcare': 'IDXHEALTH',
    'Industrials': 'IDXINDUST',
    'Infrastructures': 'IDXINFRA',
    'Property & Real Estate': 'IDXPROPERT',
    'Technology': 'IDXTECHNO',
    'Transportation & Logistic': 'IDXTRANS',
}


def extract_stocks(dataset_dir: Path) -> pd.DataFrame:
    data = []
    for dataset_path in dataset_dir.glob('*.xlsx'):
        stocks = pd.read_excel(dataset_path)
        stocks['source'] = dataset_path.name
        data.append(stocks)

    data = pd.concat(data)
    return data


def transform_stocks(data: pd.DataFrame):
    stocks = data.copy()
    stocks['code'] = stocks['Kode'] + '.JK'
    stocks['name'] = stocks['Nama Perusahaan']
    stocks['volume'] = stocks['Saham']
    stocks['sector_name'] = (
        stocks['source']
        .map(lambda val: val.split(' - ')[1])
    )
    stocks['sector_code'] = (
        stocks['sector_name']
        .map(SECTOR_MAP)
    )
    return stocks[[
        'code',
        'name',
        'volume',
        'sector_code',
        'sector_name'
    ]]


def extract_sectors(data: pd.DataFrame) -> pd.DataFrame:
    sectors = (
        data
        .groupby(['sector_code', 'sector_name'], as_index=False)
        [['code']]
        .count()
        .drop('code', axis=1)
        .rename({'sector_code': 'code', 'sector_name': 'name'}, axis=1)
    )
    return sectors


def load_sectors_to_db(
        data: pd.DataFrame,
        *,
        database: Database
        ):
    data = data.to_dict('records')
    with database.atomic():
        (
            Sector
            .insert_many(data)
            .on_conflict_ignore()
            .execute()
        )


def load_stocks_to_db(
        data: pd.DataFrame,
        *,
        database: Database,
        chunk_size: int = 64
        ):
    data = (
        data
        [['code', 'name', 'volume', 'sector_code']]
        .to_dict('records')
    )
    with database.atomic():
        for batch in chunked(data, chunk_size):
            (
                Stock
                .insert_many(batch)
                .on_conflict_ignore()
                .execute()
            )


def create_default_currencies(
        *,
        database: Database
        ):
    data = [
        {'code': 'USD', 'name': 'United States Dollar'},
        {'code': 'IDR', 'name': 'Indonesian Rupiah'},
    ]
    with database.atomic():
        (
            Currency
            .insert_many(data)
            .on_conflict_ignore()
            .execute()
        )


def create_pipeline_user(
        username: str,
        *,
        database: Database
        ) -> User:
    with database.atomic():
        user, _ = User.get_or_create(
            username=username,
            full_name=username,
            cash_balance_before=0,
            cash_balance_after=0
        )
    return user


def extract_stock_watchlist() -> list[str]:
    # Get LQ45
    res = requests.get('https://www.kontan.co.id/indeks-lq45')
    page = html.fromstring(res.text)
    rows = page.findall('.//table/tbody/tr')[:45]
    watchlist = [
        (
            row.findall('./td')[1].text_content().strip()
            + '.JK'
        )
        for row in rows
    ]
    return watchlist


def load_user_stock_watchlist_to_db(
        user: User,
        watchlist: list[str],
        *,
        database: Database
        ):
    query = Stock.select().where(Stock.code.in_(watchlist))
    with database.atomic():
        for stock in query:
            (
                UserStockWatchlist
                .insert(
                    user=user,
                    stock=stock
                )
                .on_conflict_ignore()
                .execute()
            )


def run_init_market_pipeline(args: Namespace):
    if args.debug:
        enable_debug()

    db = connect_database()

    dataset_dir = Path(args.dataset_sector)
    data = extract_stocks(dataset_dir)
    stocks = transform_stocks(data)
    sectors = extract_sectors(stocks)

    load_sectors_to_db(sectors, database=db)
    load_stocks_to_db(stocks, database=db)

    username = 'default'
    user = create_pipeline_user(username, database=db)
    watchlist = extract_stock_watchlist()
    load_user_stock_watchlist_to_db(user, watchlist, database=db)

    create_default_currencies(database=db)

