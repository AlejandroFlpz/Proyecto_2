import pandas as pd
import ta
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

from models import Operation
from port_value import get_portfolio_value
from indicators import rsi, macd, bollinger_bands
from perf_metrics import calmar_ratio


def backtest_opt(data, trial) -> float:
    

    # Params
    stop_loss = trial.suggest_float('stop_loss', 0.01, 0.12)
    take_profit = trial.suggest_float('take_profit', 0.01, 0.15)
    capital_pct_exp = trial.suggest_float('capital_pct_exp', 0.01, 0.20)

    # RSI
    rsi_window = trial.suggest_int('rsi_window', 5, 60)
    rsi_lower = trial.suggest_int('rsi_lower', 5, 35)
    rsi_upper = trial.suggest_int('rsi_upper', 60, 95)
    rsi_buy, rsi_sell = rsi(data, rsi_window, rsi_lower, rsi_upper)

    # MACD
    macd_fast = trial.suggest_int('macd_fast', 5, 20)
    macd_slow = trial.suggest_int('macd_slow', 20, 50)
    macd_signal_param = trial.suggest_int('macd_signal', 5, 20)
    macd_buy, macd_sell = macd(data, macd_fast, macd_slow, macd_signal_param)

    # Bollinger Bands
    bb_window = trial.suggest_int('bb_window', 10, 50)
    bb_window_dev = trial.suggest_float('bb_window_dev', 1.0, 3.0)
    bb_buy, bb_sell = bollinger_bands(data, bb_window, bb_window_dev)

    # Buy or sell signals
    historic = data.copy().dropna()
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
        n_shares = (cash * capital_pct_exp) / row.Close

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

        
        port_value.append(get_portfolio_value(cash,active_long_positions,active_short_positions,row.Close, COM))

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
    
    # Params from Optuna
    stop_loss = params["stop_loss"]
    take_profit = params["take_profit"]
    capital_pct_exp = params['capital_pct_exp']

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

    historic = data.copy().dropna()
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

    total_trades = 0
    wins = 0

    
    for i, row in historic.iterrows():
        n_shares = (cash * capital_pct_exp) / row.Close
        # Close LONG positions
        for position in active_long_positions.copy():
            if row.Close > position.take_profit or row.Close < position.stop_loss:

                total_trades += 1
                if row.Close > position.price:
                    wins += 1

                cash += row.Close * position.n_shares * (1 - COM)
                active_long_positions.remove(position)

        # Close SHORT positions
        for position in active_short_positions.copy():
            if row.Close < position.take_profit or row.Close > position.stop_loss:
                pnl = (position.price - row.Close) * position.n_shares * (1 - COM)

                total_trades += 1
                if pnl > 0:
                    wins += 1
                
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

        
        port_value.append(get_portfolio_value(cash,active_long_positions,active_short_positions,row.Close,COM))

    # Close Long positions at the end
    for position in active_long_positions:

        total_trades += 1
        if row.Close > position.price:
            wins += 1

        cash += row.Close * position.n_shares * (1 - COM)

    # Close Short positions at the end
    for position in active_short_positions:
        pnl = (position.price - row.Close) * position.n_shares * (1 - COM)

        total_trades += 1
        if pnl > 0:
            wins += 1

        cash += (position.price * position.n_shares * (1 + COM)) + pnl

    active_long_positions = []
    active_short_positions = []

    win_rate = (wins / total_trades) if total_trades > 0 else 0.0
    
    return port_value, cash, win_rate

def walk_forward_analysis(data, trial, n_splits: int):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    returns = []

    for train_id, test_idx in tscv.split(data):
        train_data = data.iloc[train_id]
        test_data = data.iloc[test_idx]

        score = backtest_opt(test_data, trial)
        returns.append(score)

    return sum(returns) / len(returns)


