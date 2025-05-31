from typing import Any, Type

import json
import pandas as pd
from crewai.tools import BaseTool
from datetime import datetime, timedelta
from peewee import fn
from pydantic import BaseModel, Field

from database import (
    Sector,
    Stock,
    StockDaily,
    Currency,
    CurrencyDaily,
    connect_database
)


def _calculate_change(series: pd.Series, lag: int = 1) -> float:
    return series.iloc[-1] / series.iloc[-1 - lag] - 1


def _parse_percent(value: float) -> str:
    return f'{value * 100:+.2f}%'


def _extract_trends(data: pd.DataFrame) -> str:
    data['date'] = pd.to_datetime(data['date'])
    data = data.set_index('date').resample('D').ffill()

    trends = {}
    trends['change_1d'] = _parse_percent(
        _calculate_change(data['close'])
    )
    if len(data) >= 7:
        trends['change_7d'] = _parse_percent(
            _calculate_change(data['close'], 7)
        )
    if len(data) >= 30:
        trends['change_30d'] = _parse_percent(
            _calculate_change(data['close'], 30)
        )
    if len(data) >= 60:
        trends['change_60d'] = _parse_percent(
            _calculate_change(data['close'], 60)
        )
    return json.dumps(trends)


class StockMarketShema(BaseModel):
    '''Input for StockMarketTool'''

    stock_code: str = Field(
        description='Mandatory stock code to get the recent price trends'
    )
    current_date: str = Field(
        description=
            "Mandatory current date formatted in 'YYYY-MM-DD' to be as "
            'the reference of the last date of the historical data'
    )


class StockMarketTool(BaseTool):
    '''A tool to query price trends of a stock.'''

    name: str = 'Get recent price trends of a stock'
    description: str = (
        'A tool that return recent price trends of a stock in 1D, 7D, 30D, '
        'and 60D. daily historical data of a stock. To use this '
        'tool, provide `stock_code` parameter with the code of stock you '
        'want to query and `current_date` parameter with the date formatted '
        'in `YYYY-MM-DD` to be used as a reference of the latest date.'
    )
    args_schema: Type[BaseModel] = StockMarketShema

    def _run(self, **kwargs: Any) -> str:
        stock_code = kwargs.get("stock_code")
        current_date = kwargs.get("current_date")

        if stock_code is None:
            return (
                'Error: No `stock_code` is provided. Please provide one '
                'either in the constructor or as an argument.'
            )

        if current_date is None:
            return (
                'Error: No `current_date` is provided. Please provide one '
                'either in the constructor or as an argument.'
            )

        try:
            end_date = datetime.fromisoformat(current_date)
            start_date = end_date - timedelta(days=70)
        except:
            return (
                'Error: Wrong `current_date` format. Please provide date '
                "formatted in 'YYYY-MM-DD'."
            )

        try:
            connect_database()
        except:
            return 'Error: Something went wrong while trying to connect database.'

        try:
            stock = Stock.select().where(Stock.code == stock_code).get()
        except:
            return (
                f'Error: No stock with code `{stock_code}` '
                'is available in the the database.'
            )

        try:
            data = pd.DataFrame(
                StockDaily.select()
                .where(
                    (StockDaily.stock == stock)
                    & (StockDaily.date >= start_date)
                    & (StockDaily.date <= end_date)
                )
                .order_by(StockDaily.date)
                .dicts()
            )
            if len(data) < 1:
                raise

            trends = _extract_trends(data)
        except:
            return 'Error: Something went wrong while trying to get the data.'

        return trends


class SectoralMarketShema(BaseModel):
    '''Input for SectoralkMarketTool'''

    sector_code: str = Field(
        description='Mandatory sectoral code to get the average recent price trends'
    )
    current_date: str = Field(
        description=
            "Mandatory current date formatted in 'YYYY-MM-DD' to be as "
            'the reference of the last date of the historical data'
    )


class SectoralMarketTool(BaseTool):
    '''A tool to query price trends of sectoral stocks.'''

    name: str = 'Get recent average price trends of stocks in the same sector'
    description: str = (
        'A tool that return average recent price trends of stocks in the same sector '
        'in 1D, 7D, 30D, and 60D. daily historical data of a stock. To use this '
        'tool, provide `stock_code` parameter with the code of stock you '
        'want to query and `current_date` parameter with the date formatted '
        'in `YYYY-MM-DD` to be used as a reference of the latest date.'
    )
    args_schema: Type[BaseModel] = StockMarketShema

    def _run(self, **kwargs: Any) -> str:
        sector_code = kwargs.get("sector_code")
        current_date = kwargs.get("current_date")

        if sector_code is None:
            return (
                'Error: No `sector_code` is provided. Please provide one '
                'either in the constructor or as an argument.'
            )

        if current_date is None:
            return (
                'Error: No `current_date` is provided. Please provide one '
                'either in the constructor or as an argument.'
            )

        try:
            end_date = datetime.fromisoformat(current_date)
            start_date = end_date - timedelta(days=70)
        except:
            return (
                'Error: Wrong `current_date` format. Please provide date '
                "formatted in 'YYYY-MM-DD'."
            )

        try:
            connect_database()
        except:
            return 'Error: Something went wrong while trying to connect database.'

        try:
            sector = Sector.select().where(Sector.code == sector_code).get()
        except:
            return (
                f'Error: No sector with code `{sector_code}` '
                'is available in the the database.'
            )

        try:
            data = pd.DataFrame(
                StockDaily
                .select(
                    StockDaily.date,
                    (
                        fn.SUM(StockDaily.close * Stock.volume)
                        / fn.SUM(Stock.volume)
                    ).alias('close')
                )
                .join(Stock)
                .where(
                    (Stock.sector == sector)
                    & (StockDaily.date >= start_date)
                    & (StockDaily.date <= end_date)
                )
                .group_by(StockDaily.date)
                .order_by(StockDaily.date)
                .dicts()
            )
            if len(data) < 1:
                raise

            trends = _extract_trends(data)
        except:
            return 'Error: Something went wrong while trying to get the data.'

        return trends


class CurrencyMarketShema(BaseModel):
    '''Input for CurrencyMarketTool'''

    currency_code: str = Field(
        description=
            'Mandatory 3-letter currency code to get the recent price trends '
            'compared to 1 USD'
    )
    current_date: str = Field(
        description=
            "Mandatory current date formatted in 'YYYY-MM-DD' to be as "
            'the reference of the last date of the historical data'
    )


class CurrencyMarketTool(BaseTool):
    '''A tool to query price trends of a currency.'''

    name: str = 'Get recent price trends of a currency compared to 1 USD'
    description: str = (
        'A tool that return recent price trends of a currency compared to '
        '1 USD in 1D, 7D, 30D, and 60D. To use this '
        'tool, provide `currency_code` parameter with the code of currency you '
        'want to query and `current_date` parameter with the date formatted '
        'in `YYYY-MM-DD` to be used as a reference of the latest date.'
    )
    args_schema: Type[BaseModel] = CurrencyMarketShema

    def _run(self, **kwargs: Any) -> str:
        currency_code = kwargs.get("currency_code")
        current_date = kwargs.get("current_date")

        if currency_code is None:
            return (
                'Error: No `currency_code` is provided. Please provide one '
                'either in the constructor or as an argument.'
            )

        if current_date is None:
            return (
                'Error: No `current_date` is provided. Please provide one '
                'either in the constructor or as an argument.'
            )

        try:
            end_date = datetime.fromisoformat(current_date)
            start_date = end_date - timedelta(days=70)
        except:
            return (
                'Error: Wrong `current_date` format. Please provide date '
                "formatted in 'YYYY-MM-DD'."
            )

        try:
            connect_database()
        except:
            return 'Error: Something went wrong while trying to connect database.'

        try:
            currency = (
                Currency.select()
                .where(Currency.code == currency_code)
                .get()
            )
        except:
            return (
                f'Error: No currency with code `{currency_code}` '
                'is available in the the database.'
            )

        try:
            data = pd.DataFrame(
                CurrencyDaily.select()
                .where(
                    (CurrencyDaily.from_currency_code == 'USD')
                    & (CurrencyDaily.to_currency == currency)
                    & (CurrencyDaily.date >= start_date)
                    & (CurrencyDaily.date <= end_date)
                )
                .order_by(CurrencyDaily.date)
                .dicts()
            )
            if len(data) < 1:
                raise

            trends = _extract_trends(data)
        except:
            return 'Error: Something went wrong while trying to get the data.'

        return trends
