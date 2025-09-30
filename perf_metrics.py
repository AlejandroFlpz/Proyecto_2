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
    drawdown = (rolling_max - port_value) / rolling_max
    max_drawd = drawdown.max()
    return max_drawd

def sorting_ratio(port_value: pd.Series) -> float:
    ret = port_value.pct_change().dropna()
    ret_mean = ret.mean()
    down_risk = np.minimum(ret, 0)

    annual_mean = ret_mean * 365*24
    annual_down_risk = down_risk * np.sqrt(365*24)

    if annual_down_risk > 0:
        sortino_ratio = annual_mean / annual_down_risk
    else:
        sortino_ratio = 0

    return sortino_ratio

def calmar_ratio(port_value: pd.Series) -> float:
    ret_mean = port_value.pct_change().dropna().mean()
    annual_mean = ret_mean * 365*24
    max_drawd = max_drawdown(port_value)

    if max_drawd > 0:
        calmar_ratio = annual_mean / max_drawd
    else:
        calmar_ratio = 0

    return calmar_ratio

