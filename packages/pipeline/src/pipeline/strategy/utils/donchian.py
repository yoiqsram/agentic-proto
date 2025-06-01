import pandas as pd

def _evaluate_signal(row: pd.Series) -> str:
    if row['close'] < row['rolling_min']:
        return 'Sell'
    elif row['close'] > row['rolling_max']:
        return 'Buy'
    return 'Hold'

def calculate_donchian_channel(
        df: pd.DataFrame,
        window: int = 20
    ):
    data = data[['close']].sort_index()

    data['rolling_max'] = data['close'].rolling(window=window).max()
    data['rolling_min'] = data['close'].rolling(window=window).min()
    data['rolling_range'] = data['rolling_max'] - data['rolling_min']
    data['signal'] = data.apply(_evaluate_signal, axis=1)
    data = data.drop('close', axis=1)
    
    return data