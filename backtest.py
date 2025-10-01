import pandas as pd
import ta

from models import Operation
from port_value import get_portfolio_value
from indicators import rsi, macd, bollinger_bands
from perf_metrics import ratio_de_sharpe, max_drawdown, sortino_ratio, calmar_ratio


def backtest(data, trail) -> float:
    data = data.copy()

    # Params
    stop_loss = trail.suggest_float('stop_loss', 0.01, 0.12)
    take_profit = trail.suggest_float('take_profit', 0.01, 0.15)
    n_shares = trail.suggest_int('n_shares', 0, 10)

    # RSI
    rsi_window = trail.suggest_int('rsi_window', 5, 60)
    rsi_lower = trail.suggest_int('rsi_lower', 5, 35)
    rsi_upper = trail.suggest_int('rsi_upper', 60, 95)

    rsi_buy, rsi_sell = rsi(data, rsi_window, rsi_lower, rsi_upper)

    # MACD
    macd_fast = trail.suggest_int('macd_fast', 5, 20)
    macd_slow = trail.suggest_int('macd_slow', 20, 50)
    macd_signal_param = trail.suggest_int('macd_signal', 5, 20)

    macd_buy, macd_sell = macd(data, macd_fast, macd_slow, macd_signal_param)

    # Bollinger Bands
    bb_window = trail.suggest_int('bb_window', 10, 50)
    bb_window_dev = trail.suggest_float('bb_window_dev', 1.0, 3.0)

    bb_buy, bb_sell = bollinger_bands(data, bb_window, bb_window_dev)

    # Buy or sell signals

    historic = data.dropna().copy()

    buy_signals = rsi_buy.astype(int) + macd_buy.astype(int) + bb_buy.astype(int)
    sell_signals = rsi_sell.astype(int) + macd_sell.astype(int) + bb_sell.astype(int)

    historic['buy_signal'] = buy_signals >= 2
    historic['sell_signal'] = sell_signals >= 2

    COM = 0.125 / 100
    SL = stop_loss
    TP = take_profit
    n_shares = n_shares
    cash = 1_000_000

    active_long_positions: list[Operation] = []
    active_short_positions: list[Operation] = []

    port_value = [cash]

    for i, row in historic.iterrows():

        # close positions LONG
        for position in active_long_positions.copy():

            if row.Close > position.take_profit or row.Close < position.stop_loss:
                cash += row.Close * position.n_shares * (1 - COM)
                active_long_positions.remove(position)

        # close positions LONG
        for position in active_short_positions.copy():

            if row.Close < position.take_profit or row.Close > position.stop_loss:
                cash += position.price * position.n_shares * (1 - COM)
                cash -= row.Close * position.n_shares * (1 + COM)
                active_short_positions.remove(position)

         # check signals LONG

        if not row.buy_signal:
            port_value.append(get_portfolio_value(cash, active_long_positions, active_short_positions, row.Close, n_shares, COM))
            continue

        # check if you have enough cash

        if cash < row.Close * n_shares * (1 + COM):
            port_value.append(get_portfolio_value(cash, active_long_positions, active_short_positions, row.Close, n_shares, COM))
            continue

        # discount the cost

        cash -= row.Close * n_shares * (1 + COM)

        # save the operation as active position

        active_long_positions.append(
            Operation(
                time=row.Datetime,
                price=row.Close,
                stop_loss=row.Close * (1 - SL),
                take_profit=row.Close * (1 + TP),
                n_shares=n_shares,
                type='LONG'
            )
        )

        #Check signals SHORT

        if not row.sell_signal:
            port_value.append(get_portfolio_value(cash, active_long_positions, active_short_positions, row.Close, n_shares, COM))
            continue

        # check if you have enough cash

        if cash < row.Close * n_shares * (1 + COM):
            port_value.append(get_portfolio_value(cash, active_long_positions, active_short_positions, row.Close, n_shares, COM))
            continue

        # discount the cost

        cash -= row.Close * n_shares * (1 + COM)

        # save the operation as active position

        active_short_positions.append(
            Operation(
                time=row.Datetime,
                price=row.Close,
                stop_loss=row.Close * (1 + SL),
                take_profit=row.Close * (1 - TP),
                n_shares=n_shares,
                type='SHORT'
            )
        )

        port_value.append(get_portfolio_value(cash, active_long_positions, active_short_positions, row.Close, n_shares, COM))

    # close long positions at the end
    for position in active_long_positions:
        cash += row.Close * position.n_shares * (1 - COM)

    # close short positions at the end
    for position in active_short_positions:
        cash += position.price * position.n_shares * (1 - COM)
        cash -= row.Close * position.n_shares * (1 + COM)

    active_long_positions = []
    active_short_positions = []

    calmar_df = pd.DataFrame(
        {'port_value': port_value}
    )

    calmar = calmar_ratio(calmar_df.port_value)

    return calmar
