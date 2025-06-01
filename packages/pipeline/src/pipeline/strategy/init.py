from argparse import Namespace
from enum import Enum, auto
from peewee import Database

from database import (
    Strategy as StrategyModel,
    connect_database, enable_debug
)


class Strategy(int, Enum):
    BOLLINGER_BANDS = auto()
    DONCHIAN_CHANNEL = auto()
    RELATIVE_STRENGTH_INDEX = auto()


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
    },
    Strategy.DONCHIAN_CHANNEL: {
        'name': 'Donchian Channel Breakout',
        'description':
            'The Donchian Channel is a technical analysis tool used to identify potential '
            'breakout opportunities by tracking the highest high and lowest low over a set '
            'period. It forms a price channel with three lines: the upper band (highest high), '
            'the lower band (lowest low), and the midpoint (average of the two). A breakout '
            'above the upper band signals bullish momentum, while a drop below the lower band '
            'signals bearish momentum. Traders use Donchian Channels to capture trend beginnings, '
            'manage risk, and confirm trade entries or exits based on price breakouts.'
    },
    Strategy.RELATIVE_STRENGTH_INDEX: {
        'name': 'Relative Strength Index (RSI)',
        'description':
            'The Relative Strength Index (RSI) is a momentum oscillator that measures '
            'the speed and change of price movements to evaluate overbought or oversold conditions '
            'in the price of a stock or other asset. RSI values range from 0 to 100, with levels above 70 '
            'typically indicating that an asset may be overbought and due for a correction, while levels '
            'below 30 suggest it may be oversold and poised for a rebound. RSI is calculated using the '
            'average gains and losses over a specified period, often 14 days. Traders use RSI to identify '
            'potential trend reversals, confirm price momentum, and generate buy or sell signals based on '
            'divergences between RSI and price action.',
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
