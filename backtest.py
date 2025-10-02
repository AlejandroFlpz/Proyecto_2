import pandas as pd
import ta
import numpy as np

from models import Operation
from port_value import get_portfolio_value
from indicators import rsi, macd, bollinger_bands
from perf_metrics import ratio_de_sharpe, max_drawdown, sortino_ratio, calmar_ratio


def backtest_opt(data, trail) -> float:
    

    # Params
    stop_loss = trail.suggest_float('stop_loss', 0.01, 0.12)
    take_profit = trail.suggest_float('take_profit', 0.01, 0.15)
    n_shares = trail.suggest_int('n_shares', 0, 5)

    # RSI
    rsi_window = trail.suggest_int('rsi_window', 5, 60)
    rsi_lower = trail.suggest_int('rsi_lower', 5, 35)
    rsi_upper = trail.suggest_int('rsi_upper', 60, 95)
    rsi_buy, rsi_sell = rsi(data, rsi_window, rsi_lower, rsi_upper)

    # MACD
    macd_fast = trail.suggest_int('macd_fast', 5, 20)
    macd_slow = trail.suggest_int('macd_slow', 20, 50)
    macd_signal_param = trail.suggest_int('macd_signal', 5, 20)
    macd_buy, macd_sell = macd(data, macd_fast, macd_slow, macd_signal_param)

    # Bollinger Bands
    bb_window = trail.suggest_int('bb_window', 10, 50)
    bb_window_dev = trail.suggest_float('bb_window_dev', 1.0, 3.0)
    bb_buy, bb_sell = bollinger_bands(data, bb_window, bb_window_dev)

    # Buy or sell signals
    historic = data.copy()
    historic = historic.dropna()
    buy_signals = rsi_buy.astype(int) + macd_buy.astype(int) + bb_buy.astype(int)
    sell_signals = rsi_sell.astype(int) + macd_sell.astype(int) + bb_sell.astype(int)

    historic['buy_signal'] = buy_signals >= 2
    historic['sell_signal'] = sell_signals >= 2

    
    COM = 0.125 / 100
    SL = stop_loss
    TP = take_profit
    cash = 1_000_000

    active_long_positions: list[Operation] = []
    active_short_positions: list[Operation] = []

    port_value = []

    for i, row in historic.iterrows():

        # Close LONG positions
        for position in active_long_positions.copy():
            if row.Close > position.take_profit or row.Close < position.stop_loss:
                cash += row.Close * position.n_shares * (1 - COM)
                active_long_positions.remove(position)

        # Close SHORT positions
        for position in active_short_positions.copy():
            if row.Close < position.take_profit or row.Close > position.stop_loss:
                pnl = (position.price - row.Close) * position.n_shares * (1 - COM)
                cash += (position.price * position.n_shares * (1 + COM)) + pnl
                active_short_positions.remove(position)


        # Long signal
        if row.buy_signal and cash > row.Close * n_shares * (1 + COM):
            cash -= row.Close * n_shares * (1 + COM)
            active_long_positions.append(
                Operation(
                    time=row.Datetime,
                    price=row.Close,
                    stop_loss=row.Close * (1 - SL),
                    take_profit=row.Close * (1 + TP),
                    n_shares=n_shares,
                    type='LONG'
                )
            )

        # Short signal
        if row.sell_signal and cash > row.Close * n_shares * (1 + COM):
            cash -= row.Close * n_shares * (1 + COM)
            active_short_positions.append(
                Operation(
                    time=row.Datetime,
                    price=row.Close,
                    stop_loss=row.Close * (1 + SL),
                    take_profit=row.Close * (1 - TP),
                    n_shares=n_shares,
                    type='SHORT'
                )
            )

        
        port_value.append(get_portfolio_value(cash,active_long_positions,active_short_positions,row.Close,n_shares, COM))

    # Close Long positions at the end
    for position in active_long_positions:
        cash += row.Close * position.n_shares * (1 - COM)

    # Close Short positions at the end
    for position in active_short_positions:
        pnl = (position.price - row.Close) * position.n_shares * (1 - COM)
        cash += (position.price * position.n_shares * (1 + COM)) + pnl

    
    active_long_positions = []
    active_short_positions = []

    # Calmar Ratio
    calmar_df = pd.DataFrame(
        {'port_value': port_value
    })

    calmar = calmar_ratio(calmar_df.port_value)

    return calmar




def backtest_values(data: pd.DataFrame, params: dict) -> float:
    data = data.copy()

    # Params from Optuna
    stop_loss = params["stop_loss"]
    take_profit = params["take_profit"]
    n_shares = params["n_shares"]

    rsi_window = params["rsi_window"]
    rsi_lower = params["rsi_lower"]
    rsi_upper = params["rsi_upper"]

    macd_fast = params["macd_fast"]
    macd_slow = params["macd_slow"]
    macd_signal_param = params["macd_signal"]

    bb_window = params["bb_window"]
    bb_window_dev = params["bb_window_dev"]

    rsi_buy, rsi_sell = rsi(data, rsi_window, rsi_lower, rsi_upper)
    macd_buy, macd_sell = macd(data, macd_fast, macd_slow, macd_signal_param)
    bb_buy, bb_sell = bollinger_bands(data, bb_window, bb_window_dev)

    #Sell or buy signals

    historic = data.dropna().copy()
    buy_signals = rsi_buy.astype(int) + macd_buy.astype(int) + bb_buy.astype(int)
    sell_signals = rsi_sell.astype(int) + macd_sell.astype(int) + bb_sell.astype(int)

    historic["buy_signal"] = buy_signals >= 2
    historic["sell_signal"] = sell_signals >= 2

    COM = 0.125 / 100
    SL = stop_loss
    TP = take_profit
    cash = 1_000_000

    active_long_positions: list[Operation] = []
    active_short_positions: list[Operation] = []

    port_value = []

    
    for i, row in historic.iterrows():

        # Close LONG positions
        for position in active_long_positions.copy():
            if row.Close > position.take_profit or row.Close < position.stop_loss:
                cash += row.Close * position.n_shares * (1 - COM)
                active_long_positions.remove(position)

        # Close SHORT positions
        for position in active_short_positions.copy():
            if row.Close < position.take_profit or row.Close > position.stop_loss:
                pnl = (position.price - row.Close) * position.n_shares * (1 - COM)
                cash += (position.price * position.n_shares * (1 + COM)) + pnl
                active_short_positions.remove(position)


        # Long signal
        if row.buy_signal and cash > row.Close * n_shares * (1 + COM):
            cash -= row.Close * n_shares * (1 + COM)
            active_long_positions.append(
                Operation(
                    time=row.Datetime,
                    price=row.Close,
                    stop_loss=row.Close * (1 - SL),
                    take_profit=row.Close * (1 + TP),
                    n_shares=n_shares,
                    type='LONG'
                )
            )

        # Short signal
        if row.sell_signal and cash > row.Close * n_shares * (1 + COM):
            cash -= row.Close * n_shares * (1 + COM)
            active_short_positions.append(
                Operation(
                    time=row.Datetime,
                    price=row.Close,
                    stop_loss=row.Close * (1 + SL),
                    take_profit=row.Close * (1 - TP),
                    n_shares=n_shares,
                    type='SHORT'
                )
            )

        
        port_value.append(get_portfolio_value(cash,active_long_positions,active_short_positions,row.Close,n_shares, COM))

    # Close Long positions at the end
    for position in active_long_positions:
        cash += row.Close * position.n_shares * (1 - COM)

    # Close Short positions at the end
    for position in active_short_positions:
        pnl = (position.price - row.Close) * position.n_shares * (1 - COM)
        cash += (position.price * position.n_shares * (1 + COM)) + pnl

    
    return port_value, cash