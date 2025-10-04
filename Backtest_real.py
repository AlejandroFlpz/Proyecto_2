
from models import Operation
from port_value import get_portfolio_value
import pandas as pd

def backtest(data, SL, TP, n_shares) -> pd.Series:
    data = data.copy()
    
    COM = 0.125 / 100
    stop_Loss = SL
    take_Profit = TP
    n_shares = n_shares
    cash = 1_000_000

    active_long_positions: list[Operation] = []
    active_short_positions: list[Operation] = []

    port_hist = [cash]

    for i, row in data.iterrows():

        # Close LONG positions
        for position in active_long_positions.copy():
            if (position.stop_loss > row.Close) or (position.take_profit < row.Close):
                cash += row.Close * position.n_shares * (1 - COM)
                active_long_positions.remove(position)
        
        # Close SHORT positions
        for position in active_short_positions.copy():
            if (position.stop_loss < row.Close) or (position.take_profit > row.Close):
                pnl = (position.price - row.Close) * position.n_shares * (1 - COM)
                cash += (position.price * position.n_shares) + pnl
                active_short_positions.remove(position)
        
        # Long signal
        if row.buy_signal:
                cost = row.Close * n_shares * (1 + COM)
                if cash > cost:
                    cash -= cost
                    active_long_positions.append(
                        Operation(
                            time=row.Datetime,
                            price=row.Close,
                            stop_loss=row.Close * (1 - stop_Loss),
                            take_profit=row.Close * (1 + take_Profit),
                            n_shares=n_shares,
                            type='LONG'
                )
            )

        # Short signal
        if row.sell_signal:
                cost = row.Close * n_shares * (1 + COM)
                if cash > cost:
                    cash -= cost
                    active_short_positions.append(
                        Operation(
                            time=row.Datetime,
                            price=row.Close,
                            stop_loss=row.Close * (1 + stop_Loss),
                            take_profit=row.Close * (1 - take_Profit),
                            n_shares=n_shares,
                            type='SHORT'
                )
            )
        
        port_hist.append(get_portfolio_value(cash, active_long_positions, active_short_positions, row.Close, n_shares))

    for position in active_long_positions.copy():
        cash += row.Close * position.n_shares * (1 - COM)
    
    for position in active_short_positions.copy():
        pnl = (position.price - row.Close) * position.n_shares * (1 - COM)
        cash += (position.price * position.n_shares) + pnl

    active_long_positions = []
    active_short_positions = []

    return pd.Series(port_hist)
        
                
    
    

        


