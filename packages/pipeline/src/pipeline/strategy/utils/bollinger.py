import pandas as pd
import ta


def _evaluate_signal(row: pd.Series) -> str:
    if row['close'] < row['lower_band']:
        return 'Buy'
    elif row['close'] > row['upper_band']:
        return 'Sell'
    return 'Hold'


def calculate_bollinger_bands(
        data: pd.DataFrame,
        window: int = 20
        ):
    data = data[['close']].sort_index()

    bb = ta.volatility.BollingerBands(
        close=data['close'],
        window=window
    )
    data['upper_band'] = bb.bollinger_hband()
    data['lower_band'] = bb.bollinger_lband()
    data['bandwidth'] = data['upper_band'] - data['lower_band']
    data['signal'] = data.apply(_evaluate_signal, axis=1)
    data = data.drop('close', axis=1)
    return data
