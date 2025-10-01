import pandas as pd
from data_utils import datos, split_data

def main():
    csv = 'Binance_BTCUSDT.csv'
    data = datos(csv)

    train_data, test_data, val_data = split_data(data)
    

if __name__ == "__main__":
    main()