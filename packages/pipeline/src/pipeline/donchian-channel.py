"""
-- ================================
-- 3. Donchian Channel Breakout
-- ================================
It is a trend-following trading strategy that looks for price breakouts from historical highs or lows.

Donchian Channel has 2 parts:
- Upper Band   : Highest high over the last N periods (e.g., 20 days)
- Lower Band   : Lowest low over the last N periods

Signal to action:
- Buy (Bullish breakout), when price breaks above the upper band (indicates uptrend)
- Sell (Bearish breakout), when price breaks below the lower band (indicates downtrend)
- Hold, if the price is between the bands (no breakout)

This strategy works best in trending markets and may give false signals in sideways markets.
"""

import pandas as pd

def donchian_channel_breakout(df: pd.DataFrame, window: int = 20) -> dict:
    """
    Apply Donchian Channel breakout strategy on a price series

    Parameters:
    - prices: pd.DataFrame of stock prices (Yahoo Finance)
    - window: int, number of periods to look back for high/low (default: 20)

    Returns:
    - dict with keys: ['windows', 'action']
    """

    # Flatten the multi-level columns
    df.columns = df.columns.get_level_values(1)

    # Ensure index is datetime if it's not already
    df.index = pd.to_datetime(df.index)

    # Calculate Donchian channel breakout
    recent_prices = df[-(window + 1):]['Close']
    previous_high = recent_prices[:-1].max()
    previous_low = recent_prices[:-1].min()
    current_price = recent_prices.iloc[-1]

    # Determine action
    if current_price > previous_high:
        action = 'bullish'
    elif current_price < previous_low:
        action = 'bearish'
    else:
        action = 'hold'
    
    return {'windows': window, 'action': action}