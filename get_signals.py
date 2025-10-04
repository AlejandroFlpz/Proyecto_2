from indicators import rsi_signals, ema_signals, macd_signals, bollinger_signals, stochastic_signals
import pandas as pd

def get_signal(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    data = data.copy()
    # RSI
    buy_rsi, sell_rsi = rsi_signals(
        data, 
        params['rsi_window'], 
        params['rsi_lower'], 
        params['rsi_upper']
    )

    # EMA
    buy_ema, sell_ema = ema_signals(
        data, 
        params['ema_short'], 
        params['ema_long']
    )

    # MACD
    buy_macd, sell_macd = macd_signals(
        data, 
        params['macd_fast'], 
        params['macd_slow'], 
        params['macd_signal']
    )

    # Bandas de Bollinger
    buy_bb, sell_bb = bollinger_signals(
        data,
        params['bb_window'],
        params['bb_std']
    )

    # Estocástico
    buy_stoch, sell_stoch = stochastic_signals(
        data,
        params['stoch_k_window'],
        params['stoch_d_window'],
        params['stoch_lower'],
        params['stoch_upper']
    )

    # Votación (al menos 2 de 3)
    buy_signals = buy_rsi.astype(int) + buy_ema.astype(int) + buy_macd.astype(int) + buy_bb.astype(int) + buy_stoch.astype(int)
    sell_signals = sell_rsi.astype(int) + sell_ema.astype(int) + sell_macd.astype(int) + sell_bb.astype(int) + sell_stoch.astype(int)

    data['buy_signal'] = buy_signals >= 2
    data['sell_signal'] = sell_signals >= 2

    return data
