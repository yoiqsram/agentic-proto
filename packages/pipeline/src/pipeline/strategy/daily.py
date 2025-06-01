import json
import pandas as pd
from argparse import Namespace
from datetime import datetime, timedelta
from peewee import Database
from tqdm import tqdm

from database import (
    Stock,
    StrategyEvaluation,
    connect_database, enable_debug
)

from pipeline.market.daily import extract_stock_watchlist

from .init import Strategy
from .utils.data import get_stock_daily_data
from .utils.bollinger import calculate_bollinger_bands
from .utils.donchian import calculate_donchian_channel
from .utils.rsi import calculate_rsi


def _calculate_change(series: pd.Series, lag: int = 1) -> float:
    return series.iloc[-1] / series.iloc[-1 - lag] - 1


def evaluate_bollinger_bands(
        stock: Stock,
        window: int = 20,
        *,
        database: Database
        ) -> dict:
    data = get_stock_daily_data(
        stock.code,
        start_date=datetime.now() - timedelta(days=60)
    )
    bollinger_bands = calculate_bollinger_bands(data, window)
    current_bb = bollinger_bands.iloc[-1]

    evaluation = {
        'window': window,
        'signal': current_bb['signal'],
        'current_price': data['close'].iloc[-1],
        'upper_band': current_bb['upper_band'],
        'lower_band': current_bb['lower_band'],
        'bandwidth': current_bb['bandwidth'],
        'bandwidth_change': _calculate_change(
            bollinger_bands['bandwidth'],
            window
        ),
    }

    with database.atomic():
        (
            StrategyEvaluation
            .insert(
                strategy_id=Strategy.BOLLINGER_BANDS.value,
                stock=stock,
                date=current_bb.name.strftime('%Y-%m-%d'),
                evaluation=json.dumps(evaluation)
            )
            .on_conflict_ignore()
            .execute()
        )

    return evaluation


def evaluate_donchian_channel(
        stock: Stock,
        window: int = 20,
        *,
        database: Database
        ) -> dict:
    data = get_stock_daily_data(
        stock.code,
        start_date=datetime.now() - timedelta(days=60)
    )
    donchian_channel = calculate_donchian_channel(data, window)
    current_donchian = donchian_channel.iloc[-1]

    evaluation = {
        'window': window,
        'signal': current_donchian['signal'],
        'current_price': data['close'].iloc[-1],
        'rolling_max': current_donchian['rolling_max'],
        'rolling_min': current_donchian['rolling_min'],
        'rolling_range': current_donchian['rolling_range']
    }

    with database.atomic():
        (
            StrategyEvaluation
            .insert(
                strategy_id=Strategy.DONCHIAN_CHANNEL.value,
                stock=stock,
                date=current_donchian.name.strftime('%Y-%m-%d'),
                evaluation=json.dumps(evaluation)
            )
            .on_conflict_ignore()
            .execute()
        )

    return evaluation


def evaluate_rsi(
        stock: Stock,
        lower_threshold: int = 30,
        upper_threshold: int = 70,
        *,
        database: Database
        ) -> dict:

    data = get_stock_daily_data(
        stock.code,
        start_date=datetime.now() - timedelta(days=60)
    )

    rsi = calculate_rsi(data, lower_threshold, upper_threshold)
    current_rsi = rsi.iloc[-1]

    evaluation = {
        'lower_threshold': lower_threshold,
        'upper_threshold': upper_threshold,
        'rsi': current_rsi['rsi'],
        'rsi_shifted': current_rsi['rsi_shifted'],
        'signal': current_rsi['signal'],
        'current_price': data['close'].iloc[-1],
    }

    with database.atomic():
        (
            StrategyEvaluation
            .insert(
                strategy_id=Strategy.RELATIVE_STRENGTH_INDEX.value,
                stock=stock,
                date=current_rsi.name.strftime('%Y-%m-%d'),
                evaluation=json.dumps(evaluation)
            )
            .on_conflict_ignore()
            .execute()
        )

    return evaluation


def run_daily_strategy_pipeline(args: Namespace):
    if args.debug:
        enable_debug()

    db = connect_database()

    username = 'default'
    stocks = extract_stock_watchlist(username)
    for stock in tqdm(stocks):
        evaluate_bollinger_bands(stock, database=db)
        evaluate_donchian_channel(stock, database=db)
        evaluate_rsi(stock, database=db)
