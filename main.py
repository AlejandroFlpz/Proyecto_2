
from Backtest_real import backtest
from data_utils import datos, split_data
from optimize import optimization
from get_signals import get_signal
from tablas import metric_tables
from plots import plot_portfolio_value, plot_test_validation
import optuna
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from tablas import metric_tables

def main():
    csv = 'Binance_BTCUSDT.csv'
    data = datos(csv)

    train_split, test_split, val_split = split_data(data)

    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: optimization(trial, train_split), n_trials=10)

    print(study.best_params)
    print(study.best_value)

    train_data = get_signal(train_split.copy(), study.best_params)
    portafolio_Value_train = backtest(train_data, study.best_params['stop_loss'], study.best_params['take_profit'], study.best_params['n_shares'])

    test_data = get_signal(test_split.copy(), study.best_params)
    portafolio_Value_test = backtest(test_data, study.best_params['stop_loss'], study.best_params['take_profit'], study.best_params['n_shares'])

    val_data = get_signal(val_split.copy(), study.best_params)
    portafolio_Value_val = backtest(val_data, study.best_params['stop_loss'], study.best_params['take_profit'], study.best_params['n_shares'])


    shift = portafolio_Value_test.iloc[-1] - portafolio_Value_val.iloc[0]
    portafolio_Value_val = portafolio_Value_val + shift


    test_validation = pd.concat([test_data, val_data]).reset_index(drop=True)
    total_portfolio = portafolio_Value_test + portafolio_Value_val

    plot_portfolio_value(portafolio_Value_train)
    plot_test_validation(portafolio_Value_test, portafolio_Value_val, test_data, val_data)

if __name__ == "__main__":
    main()

