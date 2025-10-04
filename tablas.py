from perf_metrics import ratio_de_sharpe, max_drawdown, sortino_ratio, calmar_ratio
import pandas as pd

def metrics(port_value: pd.Series) -> pd.DataFrame:
    metrics = pd.DataFrame({
        "Ratio de Sharpe": [ratio_de_sharpe(port_value)],
        "Max Drawdown": [max_drawdown(port_value)],
        "Sortino Ratio": [sortino_ratio(port_value)],
        "Calmar Ratio": [calmar_ratio(port_value)],
    }, index=["Metrics"])

    return metrics

def returns(portfolio_Value_test, portfolio_Value_val, test_split, val_split) -> tuple[pd.Series, pd.DataFrame]:

    test_validation = pd.concat([test_split, val_split]).reset_index(drop=True)
    total_portfolio = portfolio_Value_test + portfolio_Value_val

   
    dates = test_validation['Datetime'].tail(len(total_portfolio)).reset_index(drop=True)
    port_val_idx_dates = pd.DataFrame({
        'Datetime': dates,
        'Portfolio_Value': total_portfolio
    })


    port_val_idx_dates = port_val_idx_dates.copy().assign(Datetime=pd.to_datetime(port_val_idx_dates['Datetime'])).set_index('Datetime')

    
    port_val_idx_dates['Returns'] = port_val_idx_dates['Portfolio_Value'].pct_change(fill_method=None)
    monthly_returns = port_val_idx_dates['Returns'].resample('ME').apply(lambda x: (1 + x).prod() - 1)
    quarterly_returns = port_val_idx_dates['Returns'].resample('QE').apply(lambda x: (1 + x).prod() - 1)
    annually_returns = port_val_idx_dates['Returns'].resample('YE').apply(lambda x: (1 + x).prod() - 1)

    
    port_val_through_time = pd.DataFrame({
        "Monthly_Returns": monthly_returns,
        "Quarterly_Returns": quarterly_returns,
        "Annually_Returns": annually_returns
    })

    port_val_through_time = port_val_through_time.fillna(0)

    return total_portfolio, port_val_through_time