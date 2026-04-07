import pandas as pd
from ml_logic import XGBoostPredictor

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
    def __init__(self, window=20, threshold=0.02):
        super().__init__(name=f"Mean Reversion ({threshold*100:.0f}%)")
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

class XGBoostStrategy(BaseStrategy):
    def __init__(self, window=20, threshold=0.02):
        super().__init__(name="XGBoost + Mean Reversion")
        self.window = window
        self.threshold = threshold
        self.predictors = {} # Un predictor por cada moneda

    def generate_signals(self, data, symbol=None):
        if len(data) < self.window:
            return 'hold'

        # Si no se pasa símbolo, cae en la lógica normal de Mean Reversion
        if not symbol:
            # Calcular media móvil simple (SMA)
            data['sma'] = data['close'].rolling(window=self.window).mean()
            last_row = data.iloc[-1]
            current_price = last_row['close']
            sma_value = last_row['sma']

            if current_price < sma_value * (1 - self.threshold):
                return 'buy'
            elif current_price > sma_value * (1 + self.threshold):
                return 'sell'
            return 'hold'

        # Inicializar predictor si no existe para este símbolo
        if symbol not in self.predictors:
            self.predictors[symbol] = XGBoostPredictor(symbol)
        
        predictor = self.predictors[symbol]
        
        # 1. Análisis Técnico (Mean Reversion)
        data['sma'] = data['close'].rolling(window=self.window).mean()
        last_row = data.iloc[-1]
        current_price = last_row['close']
        sma_value = last_row['sma']
        
        # 2. Análisis de ML (Predicción)
        prediction_data = predictor.predict(data)
        
        ml_prediction = None
        ml_confidence = 0
        
        if prediction_data:
            ml_prediction, ml_confidence = prediction_data

        # Lógica Híbrida:
        # COMPRA: Precio bajo la media Y modelo predice subida (1) con confianza > 52%
        if current_price < sma_value * (1 - self.threshold):
            if ml_prediction == 1 and ml_confidence > 0.52:
                return 'buy'
            else:
                return 'hold' # Filtramos la compra si la IA no está segura

        # VENTA: Precio sobre la media Y modelo predice bajada (0) con confianza > 52% (prob subida < 48%)
        elif current_price > sma_value * (1 + self.threshold):
            if ml_prediction == 0 and ml_confidence < 0.48:
                return 'sell'
            else:
                return 'hold' # Filtramos la venta si la IA no está segura
        
        return 'hold'
