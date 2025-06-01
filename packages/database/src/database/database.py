from peewee import (
    Model as DBModel,
    AutoField,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    IntegerField,
    BigIntegerField,
    FloatField,
    ForeignKeyField,
    TextField,
    SQL,
    SqliteDatabase
)


def enable_debug():
    import logging
    logger = logging.getLogger('peewee')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)


class User(DBModel):
    id = AutoField()
    username = CharField(unique=True)
    full_name = CharField()
    cash_balance_before = FloatField()
    cash_balance_after = FloatField()
    created_datetime = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )
    modified_datetime = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )


class UserBalance(DBModel):
    id = AutoField()
    user = ForeignKeyField(
        User,
        column_name='user_id',
        backref='cash_balance_history',
        unique=True
    )
    cash_balance_before = FloatField()
    cash_balance_after = FloatField()
    remark = CharField(null=True)
    created_datetime = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )

    class Meta:
        db_table = 'user_balance'


class Sector(DBModel):
    code = CharField(unique=True)
    name = CharField(unique=True)


class Stock(DBModel):
    code = CharField(unique=True)
    name = CharField()
    volume = BigIntegerField()
    sector = ForeignKeyField(
        Sector,
        Sector.code,
        column_name='sector_code',
        backref='stocks'
    )


class StockDaily(DBModel):
    id = AutoField()
    stock = ForeignKeyField(
        Stock,
        Stock.code,
        column_name='stock_code',
        backref='daily_history'
    )
    date = DateField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = BigIntegerField()
    created_datetime = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )

    class Meta:
        db_table = 'stock_price_daily'
        indexes = ((('stock_code', 'date'), True),)


class Currency(DBModel):
    code = CharField(unique=True)
    name = CharField()


class CurrencyDaily(DBModel):
    id = AutoField()
    from_currency = ForeignKeyField(
        Currency,
        Currency.code,
        column_name='from_currency_code'
    )
    to_currency = ForeignKeyField(
        Currency,
        Currency.code,
        column_name='to_currency_code'
    )
    date = DateField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    created_datetime = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )

    class Meta:
        db_table = 'currency_daily'
        indexes = ((('from_currency_code', 'to_currency_code', 'date'), True),)


class UserStockTrade(DBModel):
    id = AutoField()
    user = ForeignKeyField(
        User,
        column_name='user_id',
        backref='trade_history',
        unique=True
    )
    stock = ForeignKeyField(
        Stock,
        Stock.code,
        column_name='stock_code',
        backref='trade_history'
    )
    is_buy = BooleanField()
    amount = IntegerField()
    price = IntegerField()
    commission_fee = FloatField()
    executed_datetime = DateTimeField(null=True)
    created_datetime = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )
    modified_datetime = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )

    class Meta:
        db_table = 'stock_trade'


class UserStockWatchlist(DBModel):
    id = AutoField()
    user = ForeignKeyField(
        User,
        column_name='user_id',
        backref='watchlist'
    )
    stock = ForeignKeyField(
        Stock,
        Stock.code,
        column_name='stock_code'
    )
    created_datetime = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )

    class Meta:
        db_table = 'stock_watchlist'
        indexes = ((('user_id', 'stock_code'), True),)


class Strategy(DBModel):
    id = AutoField()
    name = CharField(unique=True)
    description = CharField(null=True)


class StrategyEvaluation(DBModel):
    id = AutoField()
    strategy = ForeignKeyField(
        Strategy,
        column_name='strategy_id'
    )
    stock = ForeignKeyField(
        Stock,
        Stock.code,
        column_name='stock_code'
    )
    date = DateField()
    evaluation = TextField()
    created_datetime = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )

    class Meta:
        db_table = 'strategy_evaluation'
        indexes = ((('strategy_id', 'stock_code', 'date'), True),)


db_models = [
    User,
    UserBalance,
    Sector,
    Stock,
    StockDaily,
    Currency,
    CurrencyDaily,
    UserStockTrade,
    UserStockWatchlist,
    Strategy,
    StrategyEvaluation
]


def _get_database(database: str | None = None) -> SqliteDatabase:
    if database is None:
        database = SqliteDatabase('app.db')
    else:
        database = SqliteDatabase(database)
    return database


def connect_database(database: str | None = None) -> SqliteDatabase:
    database = _get_database(database)
    database.bind(db_models)
    return database


def create_database(database: str | None = None) -> SqliteDatabase:
    database = _get_database(database)
    database.bind(db_models)
    database.create_tables(db_models)
    return database
