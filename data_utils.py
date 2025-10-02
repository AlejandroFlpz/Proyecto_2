import pandas as pd


def datos(csv: str) -> pd.DataFrame:
    data = pd.read_csv(csv).dropna()
    data = data.copy()
    data = data.rename(columns={'Date': 'Datetime'})
    data['Datetime'] = pd.to_datetime(data['Datetime'], errors='coerce', dayfirst=True)
    data = data.iloc[::-1].reset_index(drop=True)

    return data

def split_data(data: pd.DataFrame):
    train_size = int(len(data) * 0.6)
    test_size = int(len(data) * 0.2)

    train_data = data.iloc[:train_size]
    test_data = data.iloc[train_size:train_size + test_size]
    val_data = data.iloc[train_size + test_size:]


    return train_data, test_data, val_data


