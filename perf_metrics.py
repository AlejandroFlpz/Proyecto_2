import pandas as pd
import numpy as np



def ratio_de_sharpe(port_value: pd.Series) -> float:
    ret_mean = port_value.pct_change().dropna().mean()
    ret_std = port_value.pct_change().dropna().std()

    annual_mean = ret_mean * 365*24
    annual_std = ret_std * np.sqrt(365*24)
    if annual_std > 0:
        sharpe = annual_mean / annual_std
    else:
        sharpe = 0

    return sharpe

def max_drawdown(port_value: pd.Series) -> float:
    rolling_max = port_value.cummax()
    drawdown = (port_value - rolling_max) / rolling_max
    max_drawdwn = drawdown.min()
    return max_drawdwn

def sortino_ratio(port_value: pd.Series) -> float:
    ret = port_value.pct_change().dropna()
    ret_mean = ret.mean()
    downside_vol = np.minimum(ret, 0)

    annual_mean = ret_mean * 365*24
    annual_downside_vol = downside_vol * np.sqrt(365*24)

    if annual_downside_vol > 0:
        sortino = annual_mean / annual_downside_vol
    else:
        sortino = 0

    return sortino

def calmar_ratio(port_value: pd.Series) -> float:
    ret_mean = port_value.pct_change().dropna().mean()
    annual_mean = ret_mean * 365*24
    max_drawd = max_drawdown(port_value)

    if max_drawd > 0:
        calmar = annual_mean / max_drawd
    else:
        calmar = 0

    return calmar
