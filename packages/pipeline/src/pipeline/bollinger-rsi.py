"""
-- ===============================
-- 1. Bollinger Bands Reversal
-- ===============================
It is a trading strategy to see how high the stock price compared to its average.
Bollinger band has 3 parts :
- Middle Band   : Moving average, usually use window 20
- Lower Band    : Middle band - 2 standard deviations
- Upper Band    : Middle band + 2 standard deviations

Signal to action:
- Buy, when price touches or goes below than the lower band (start moving up)
- Sell, when price touches or goes above than the upper band (start moving down)

-- ==============================================
-- 2. Relative Strength Index (RSI) Reversion
-- ==============================================
It is a trading indicator to measure the price is overbought (too expensive) or oversold (too cheap).

RSI has range between 0 to 100 with these threshold:
- 70 and above, overbougt
- 30 and below, oversold

Signal to action:
- Buy, when price touches 30 and below (start moving up)
- Sell, when price touches 70 and above (start moving down)
"""

# Import the libraries
import yfinance as yf
import pandas as pd
import ta

# Bollinger bands flag
def indicator_flag(row):
    if row['buy_signal']:
        return "Beli"
    elif row['sell_signal']:
        return "Jual"
    else:
        return "Diam"
    
# Bollinger bands action
def bollinger_bands_action(df, window=20):

    # Flatten the multi-level columns
    df.columns = df.columns.get_level_values(1)

    # Ensure index is datetime if it's not already
    df.index = pd.to_datetime(df.index)

    # Sort index (optional, good practice)
    df = df.sort_index().loc[:, ['Close']]

    # Calculate Bollinger Bands
    bb = ta.volatility.BollingerBands(close=df["Close"], window=window)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()

    # Signal to action
    df['buy_signal'] = df['Close'] < df['bb_lower']
    df['sell_signal'] = df['Close'] < df['bb_upper']
    df['action'] = df.apply(indicator_flag, axis=1)
    
    return df['action'], df['bb_upper'], df['bb_lower']

# RSI action
def rsi_action(df, lower_threshold=30, upper_threshold=70):

    # Flatten the multi-level columns
    df.columns = df.columns.get_level_values(1)

    # Ensure index is datetime if it's not already
    df.index = pd.to_datetime(df.index)

    # Sort index (optional, good practice)
    df = df.sort_index().loc[:, ['Close']]

    # Calculate RSI
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()

    # Signal to action
    df['buy_signal'] = (df['RSI'] < lower_threshold) & (df['RSI'].shift(1) < df['RSI'])
    df['sell_signal'] = (df['RSI'] > upper_threshold) & (df['RSI'].shift(1) > df['RSI'])
    df['action'] = df.apply(indicator_flag, axis=1)
    
    return df['action'], df['RSI']

# # Download stock data
# df = yf.download("AAPL", group_by='Ticker', auto_adjust=False, start="2023-01-01", end="2024-01-01")
# bollinger_bands_action(df)[0]
# rsi_action(df)[0]