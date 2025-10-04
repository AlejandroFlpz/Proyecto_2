
from Backtest_real import backtest
from data_utils import datos, split_data
from optimize import optimization
from get_signals import get_signal
from tablas import metric_tables
from plots import plot_portfolio_value_train, plot_test_validation
import optuna
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from tablas import metric_tables

def main():

    # Data
    csv = 'Binance_BTCUSDT.csv'
    data = datos(csv)

    # Split data

    train_split, test_split, val_split = split_data(data)

    # Optimization

    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: optimization(trial, train_split), n_trials=10)

    print("\n Mejores parámetros encontrados:")
    print(study.best_params)
    print(f"Mejor valor objetivo: {study.best_value:.4f}\n")

    # Training results

    print("────────────── TRAIN RESULTS ──────────────")

    train_data = get_signal(train_split.copy(), study.best_params)
    portafolio_Value_train, cash_train, win_rate_train = backtest(train_data, cash=1_000_000, params=study.best_params)

    print(f"Portfolio Value Final: {portafolio_Value_train.iloc[-1]:,.2f}")
    print(f"Cash Final: {cash_train:,.2f}")
    print(f"Win Rate: {win_rate_train:.2%}")
    print(metric_tables(portafolio_Value_train))    
    print("\n")

    # Test results

    print("────────────── TEST RESULTS ──────────────")

    test_data = get_signal(test_split.copy(), study.best_params)
    portafolio_Value_test, cash_test, win_rate_test = backtest(test_data, cash=1_000_000, params=study.best_params)

    print(f"Portfolio Value Final: {portafolio_Value_test.iloc[-1]:,.2f}")
    print(f"Cash Final: {cash_test:,.2f}")
    print(f"Win Rate: {win_rate_test:.2%}")
    print(metric_tables(portafolio_Value_test))
    print("\n")

    # Validation results

    print("────────────── VALIDATION RESULTS ──────────────")

    val_data = get_signal(val_split.copy(), study.best_params)
    portafolio_Value_val, cash_val, win_rate_val = backtest(val_data, cash=cash_test, params=study.best_params)

    print(f"Portfolio Value inicial: {portafolio_Value_val.iloc[0]:,.2f}")
    print(f"Portfolio Value Final: {portafolio_Value_val.iloc[-1]:,.2f}")
    print(f"Cash Final: {cash_val:,.2f}")
    print(f"Win Rate: {win_rate_val:.2%}")
    print(metric_tables(portafolio_Value_val))
    print("\n")

    # Plots
    plt.plot(portafolio_Value_test)
    plt.plot(portafolio_Value_val)
    plt.show()


if __name__ == "__main__":
    main()

