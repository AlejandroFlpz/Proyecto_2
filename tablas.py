from perf_metrics import ratio_de_sharpe, max_drawdown, sortino_ratio, calmar_ratio
import pandas as pd

def metric_tables(port_value):
    metrics = pd.DataFrame({
        "Ratio de Sharpe": [ratio_de_sharpe(port_value)],
        "Max Drawdown": [max_drawdown(port_value)],
        "Sortino Ratio": [sortino_ratio(port_value)],
        "Calmar Ratio": [calmar_ratio(port_value)]
    })

    return metrics