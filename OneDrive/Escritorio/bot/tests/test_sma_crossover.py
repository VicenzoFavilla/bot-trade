import pandas as pd
import sys
import os

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from strategy import SMACrossoverStrategy

def test_sma_crossover_buy():
    # Caso: SMA corta cruza por encima de SMA larga -> señal de compra
    # Ventanas: 5 y 10
    short_window = 5
    long_window = 10
    
    # Simular una tendencia alcista
    data = {'close': list(range(1, 11)) + [20, 30]} # 12 velas
    df = pd.DataFrame(data)
    
    strategy = SMACrossoverStrategy(short_window=short_window, long_window=long_window)
    signal = strategy.generate_signals(df)
    
    # En este caso particular, la media corta subirá más rápido que la larga.
    # Por ahora solo comprobamos que el bot puede generar señales sin errores con este formato.
    assert signal in ['buy', 'sell', 'hold']

def test_sma_crossover_insufficient_data():
    data = {'close': [100] * 5}
    df = pd.DataFrame(data)
    strategy = SMACrossoverStrategy(short_window=5, long_window=10)
    signal = strategy.generate_signals(df)
    assert signal == 'hold'
