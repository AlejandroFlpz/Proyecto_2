from Backtest_real import backtest
from perf_metrics import calmar_ratio
from get_signals import get_signals
import pandas as pd
import numpy as np

def optimization(trial, train_data):
    data = train_data.copy() 

    # RSI
    rsi_window = trial.suggest_int('rsi_window', 5, 60)
    rsi_lower = trial.suggest_int('rsi_lower', 5, 35)
    rsi_upper = trial.suggest_int('rsi_upper', 60, 95)

    # MACD
    macd_fast = trial.suggest_int('macd_fast', 5, 20)
    macd_slow = trial.suggest_int('macd_slow', 20, 50)
    macd_signal_param = trial.suggest_int('macd_signal', 5, 20)

    # Bollinger Bands
    bb_window = trial.suggest_int('bb_window', 10, 50)
    bb_window_dev = trial.suggest_float('bb_window_dev', 1.0, 3.0)

    # Params
    stop_loss = trial.suggest_float('stop_loss', 0.01, 0.12)
    take_profit = trial.suggest_float('take_profit', 0.01, 0.15)
    n_shares = trial.suggest_float('n_shares', 0.01, 5)

    params = {
        'rsi_window': rsi_window,
        'rsi_lower': rsi_lower,
        'rsi_upper': rsi_upper,
        'macd_fast': macd_fast,
        'macd_slow': macd_slow,
        'macd_signal': macd_signal_param,
        'bb_window': bb_window,
        'bb_window_dev': bb_window_dev,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'n_shares': n_shares
    }

    # Generar señales usando los params
    data = get_signals(data, params)

    # Cross-validation
    n_splits = 5
    len_data = len(data)
    calmars = []

    for i in range(n_splits):
        size = len_data // n_splits
        start_idx = i * size
        end_idx = (i + 1) * size
        chunk = data.iloc[start_idx:end_idx, :]

        port_vals = backtest(chunk, params['stop_loss'], params['take_profit'], params['n_shares'])
        calmar = calmar_ratio(port_vals)
        calmars.append(calmar)
    
    return np.mean(calmars)
