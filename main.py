
from Backtest_real import backtest
from data_utils import datos, split_data
from optimize import optimization
from get_signals import get_signals
import optuna
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    csv = 'Binance_BTCUSDT.csv'
    data = datos(csv)

    train_data, test_data, val_data = split_data(data)

    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: optimization(trial, train_data), n_trials=20, n_jobs=-1)

    print(study.best_params)
    print(study.best_value)

    train_data = get_signals(train_data.copy(), study.best_params)
    portafolio_Value = backtest(train_data, study.best_params['stop_loss'], study.best_params['take_profit'], study.best_params['n_shares'])

    plt.figure(figsize=(12, 6))
    plt.plot(portafolio_Value, label='Portfolio Value')
    plt.title('Portfolio Value Over Time')
    plt.xlabel('Time')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()