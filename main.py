
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

    train_data = get_signal(train_split.copy(), study.best_params)
    portafolio_Value_train, cash_train, win_rate_train = backtest(train_data, study.best_params)

    print("Portfolio value: ", portafolio_Value_train.iloc[-1])
    
    print("Cash: ", cash_train)

    print(f"Win rate: {win_rate_train:.2%}")

    print(metric_tables(portafolio_Value_train))

    # Test results

    test_data = get_signal(test_split.copy(), study.best_params)
    portafolio_Value_test, cash_test, win_rate_test = backtest(test_data, study.best_params)


    print("Portfolio value: ", portafolio_Value_test.iloc[-1])

    print("Cash: ", cash_test)

    print(f"Win rate: {win_rate_test:.2%}")

    print(metric_tables(portafolio_Value_test))

    # Validation results

    val_data = get_signal(val_split.copy(), study.best_params)
    portafolio_Value_val, cash_val, win_rate_val = backtest(val_data, study.best_params)

    print("Cash: ", cash_val)

    print("Portfolio value: ", portafolio_Value_val.iloc[-1])

    print(f"Win rate: {win_rate_val:.2%}")

    print(metric_tables(portafolio_Value_val))


    shift = portafolio_Value_test.iloc[-1] - portafolio_Value_val.iloc[0]
    portafolio_Value_val = portafolio_Value_val + shift


    test_validation = pd.concat([test_data, val_data]).reset_index(drop=True)
    total_portfolio = portafolio_Value_test + portafolio_Value_val


    #Plots

    plot_portfolio_value_train(portafolio_Value_train)
    plot_test_validation(portafolio_Value_test, portafolio_Value_val, test_data, val_data)

if __name__ == "__main__":
    main()

