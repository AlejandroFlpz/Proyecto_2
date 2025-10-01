from models import Operation

def get_portfolio_value(cash: float, long_ops: list[Operation], short_ops: list[Operation], current_price: float, n_shares: int, COM: float) -> float:
    val = cash

    # add long positions value
    val += len(long_ops) * n_shares * current_price

    # add short positions value
    
    for position in short_ops:
        p_l += (position.price - current_price) * position.n_shares * (1-COM)
        val += p_l

    return val
