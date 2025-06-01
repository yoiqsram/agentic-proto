from argparse import Namespace
from enum import Enum, auto
from peewee import Database

from database import (
    Strategy as StrategyModel,
    connect_database, enable_debug
)


class Strategy(int, Enum):
    BOLLINGER_BANDS = auto()


STRATEGIES = {
    Strategy.BOLLINGER_BANDS: {
        'name': 'Bollinger Bands',
        'description':
            'Bollinger Bands are a technical analysis tool used to measure market '
            'volatility and identify potential overbought or oversold conditions. '
            'They consist of three lines: a simple moving average (SMA) in the '
            'middle, and two outer bands that are typically set two standard '
            'deviations above and below the SMA. When prices move closer to the '
            'upper band, the asset may be overbought; near the lower band, it may '
            'be oversold. Traders use Bollinger Bands to spot trend reversals, '
            'breakouts, and to gauge price momentum.',
    }
}


def create_strategies(
        *,
        database: Database
        ):
    data = [
        {
            'id': strategy.value,
            'name': name,
            'description': description
        }
        for strategy, (name, description) in STRATEGIES.items()
    ]
    with database.atomic():
        (
            StrategyModel
            .insert_many(data)
            .on_conflict_ignore()
            .execute()
        )


def run_init_strategy_pipeline(args: Namespace):
    if args.debug:
        enable_debug()

    db = connect_database()

    create_strategies(database=db)
