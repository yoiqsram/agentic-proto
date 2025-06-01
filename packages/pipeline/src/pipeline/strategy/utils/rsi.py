import pandas as pd
import ta


def _evaluate_signal(row: pd.Series, lower_threshold: int, upper_threshold: int) -> str:
    if (row['close'] < lower_threshold) & (row['rsi'] > row['rsi_shifted']):
        return 'Buy'
    elif (row['close'] > upper_threshold) & (row['rsi'] < row['rsi_shifted']):
        return 'Sell'
    return 'Hold'


def calculate_rsi(
        data: pd.DataFrame,
        lower_threshold: int = 30,
        upper_threshold: int = 70
        ):

    data = data[['close']].sort_index()
    data['rsi'] = ta.momentum.RSIIndicator(data['close']).rsi()
    data['rsi_shifted'] = data['rsi'].shift(1)
    data['signal'] = data.apply(lambda row: _evaluate_signal(row, lower_threshold, upper_threshold), axis=1)
    data = data.drop('close', axis=1)

    return data