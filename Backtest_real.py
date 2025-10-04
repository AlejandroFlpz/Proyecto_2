
from models import Operation
from port_value import get_portfolio_value
import pandas as pd

def backtest(data, params:dict) -> tuple[pd.Series, float, float]:
    data = data.copy()
    
    COM = 0.125 / 100
    stop_Loss = params['stop_loss']
    take_Profit = params['take_profit']
    n_shares = params['n_shares']
    cash = 1_000_000

    active_long_positions: list[Operation] = []
    active_short_positions: list[Operation] = []

    port_hist = [cash]

    total_trades = 0
    wins = 0

    for i, row in data.iterrows():

        # Close LONG positions
        for position in active_long_positions.copy():
            if (position.stop_loss > row.Close) or (position.take_profit < row.Close):
                pnl = (row.Close - position.price) * position.n_shares * (1 - COM)
                if pnl > 0:
                    wins += 1
                total_trades += 1
                cash += row.Close * position.n_shares * (1 - COM)
                active_long_positions.remove(position)

        
        # Close SHORT positions
        for position in active_short_positions.copy():
            if (position.stop_loss < row.Close) or (position.take_profit > row.Close):
                pnl = (position.price - row.Close) * position.n_shares * (1 - COM)
                if pnl > 0:
                    wins += 1
                total_trades += 1
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
        pnl = (row.Close - position.price) * position.n_shares * (1 - COM)
        if pnl > 0:
            wins += 1
        total_trades += 1
        cash += row.Close * position.n_shares * (1 - COM)
    
    for position in active_short_positions.copy():
        pnl = (position.price - row.Close) * position.n_shares * (1 - COM)
        if pnl > 0:
            wins += 1
        total_trades += 1
        cash += (position.price * position.n_shares) + pnl

    active_long_positions = []
    active_short_positions = []

    win_rate = wins / total_trades if total_trades > 0 else 0

    return pd.Series(port_hist), cash, win_rate

    

        


