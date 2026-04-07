import pandas as pd

class BaseStrategy:
    def __init__(self, name="BaseStrategy"):
        self.name = name

    def generate_signals(self, data):
        """
        Debe devolver 'buy', 'sell' o 'hold'.
        'data' es un DataFrame de pandas con columnas: timestamp, open, high, low, close, volume.
        """
        raise NotImplementedError("Cada estrategia debe implementar generate_signals")

class SMACrossoverStrategy(BaseStrategy):
    def __init__(self, short_window=10, long_window=50):
        super().__init__(name="SMA Crossover")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data):
        if len(data) < self.long_window:
            return 'hold'

        # Calcular medias móviles
        data['sma_short'] = data['close'].rolling(window=self.short_window).mean()
        data['sma_long'] = data['close'].rolling(window=self.long_window).mean()

        last_row = data.iloc[-1]
        prev_row = data.iloc[-2]

        # Lógica de cruce
        if prev_row['sma_short'] <= prev_row['sma_long'] and last_row['sma_short'] > last_row['sma_long']:
            return 'buy'
        elif prev_row['sma_short'] >= prev_row['sma_long'] and last_row['sma_short'] < last_row['sma_long']:
            return 'sell'
        
        return 'hold'

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, window=20, threshold=0.05):
        super().__init__(name="Mean Reversion (5%)")
        self.window = window
        self.threshold = threshold

    def generate_signals(self, data):
        if len(data) < self.window:
            return 'hold'

        # Calcular media móvil simple (SMA)
        data['sma'] = data['close'].rolling(window=self.window).mean()
        
        last_row = data.iloc[-1]
        current_price = last_row['close']
        sma_value = last_row['sma']

        # Lógica de porcentaje respecto a la media
        # Si baja de la media un 5% (u otro umbral configurable) -> Comprar
        if current_price < sma_value * (1 - self.threshold):
            return 'buy'
        # Si sube de la media un 5% (u otro umbral configurable) -> Vender
        elif current_price > sma_value * (1 + self.threshold):
            return 'sell'
        
        return 'hold'
