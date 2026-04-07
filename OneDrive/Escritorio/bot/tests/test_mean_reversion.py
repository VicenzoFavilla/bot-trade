import pandas as pd
import sys
import os

# Añadir el directorio src al path para que coincida con la estructura del proyecto
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from strategy import MeanReversionStrategy

def test_mean_reversion_hold():
    # Caso 1: Precio en la media
    data = {'close': [100] * 20}
    df = pd.DataFrame(data)
    strategy = MeanReversionStrategy(window=20, threshold=0.05)
    signal = strategy.generate_signals(df)
    assert signal == 'hold'

def test_mean_reversion_buy():
    # Caso 2: Precio baja más del 5% (e.g., 94)
    data = {'close': [100] * 19 + [94]}
    df = pd.DataFrame(data)
    strategy = MeanReversionStrategy(window=20, threshold=0.05)
    signal = strategy.generate_signals(df)
    assert signal == 'buy'

def test_mean_reversion_sell():
    # Caso 3: Precio sube más del 5% (e.g., 106)
    data = {'close': [100] * 19 + [106]}
    df = pd.DataFrame(data)
    strategy = MeanReversionStrategy(window=20, threshold=0.05)
    signal = strategy.generate_signals(df)
    assert signal == 'sell'

def test_insufficient_data():
    # Caso: No hay suficientes datos para la ventana
    data = {'close': [100] * 10}
    df = pd.DataFrame(data)
    strategy = MeanReversionStrategy(window=20, threshold=0.05)
    signal = strategy.generate_signals(df)
    assert signal == 'hold'
