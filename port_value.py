from models import Operation

def get_portfolio_value(cash: float, long_ops: list[Operation], short_ops: list[Operation], current_price: float, n_shares: int, COM: float) -> float:
    val = cash

    # add long positions value
    for position in long_ops:
        val += current_price * position.n_shares * (1 - COM)

    # add short positions value
    
    for position in short_ops:
        pnl = (position.price - current_price) * position.n_shares * (1 - COM)
        val += ((position.price * position.n_shares * (1 + COM)) + pnl)

    return val


