
from data_utils import datos, split_data
from backtest import backtest_opt, backtest_values
import optuna
import pandas as pd
import matplotlib.pyplot as plt

def main():
    csv = 'Binance_BTCUSDT.csv'
    data = datos(csv)

    train_data, test_data, val_data = split_data(data)

    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trail: backtest_opt(train_data, trail), n_trials=10)

    port_value_t, cash_t = backtest_values(train_data, study.best_params)

    print(port_value_t)
    print(cash_t)

    plt.plot(port_value_t)
    plt.title('Portfolio Value Over Time')
    plt.xlabel('Time')      
    plt.ylabel('Portfolio Value')
    plt.show(block=False)
    plt.pause(10)   
    plt.close()


if __name__ == "__main__":
    main()