import pandas as pd
import numpy as np
import xgboost as xgb
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator
from ta.volatility import AverageTrueRange
import joblib
import os
import logging

class XGBoostPredictor:
    def __init__(self, symbol):
        self.symbol = symbol.replace('/', '_')
        self.model = None
        self.features = [
            'rsi', 'sma_dist', 'ema_dist', 'volatility', 
            'return_1', 'return_5', 'volume_change'
        ]

    def prepare_features(self, df):
        """Genera indicadores técnicos como features para el modelo."""
        data = df.copy()
        
        # Indicadores base
        data['rsi'] = RSIIndicator(close=data['close']).rsi()
        data['sma_20'] = SMAIndicator(close=data['close'], window=20).sma_indicator()
        data['ema_10'] = EMAIndicator(close=data['close'], window=10).ema_indicator()
        data['atr'] = AverageTrueRange(high=data['high'], low=data['low'], close=data['close']).average_true_range()
        
        # Features relativas (más estables para ML)
        data['sma_dist'] = (data['close'] - data['sma_20']) / data['sma_20']
        data['ema_dist'] = (data['close'] - data['ema_10']) / data['ema_10']
        data['volatility'] = data['atr'] / data['close']
        
        # Retornos y cambios de volumen
        data['return_1'] = data['close'].pct_change(1)
        data['return_5'] = data['close'].pct_change(5)
        data['volume_change'] = data['volume'].pct_change(1)
        
        # Target: 1 si el precio sube en la siguiente vela, 0 si baja
        data['target'] = (data['close'].shift(-1) > data['close']).astype(int)
        
        # LIMPIEZA CRÍTICA: Reemplazar infinitos por NaN y luego eliminarlos
        data = data.replace([np.inf, -np.inf], np.nan)
        return data.dropna()

    def train(self, df):
        """Entrena el modelo XGBoost con los datos proporcionados."""
        try:
            processed_data = self.prepare_features(df)
            if len(processed_data) < 100:
                logging.warning(f"[{self.symbol}] Datos insuficientes para entrenar ({len(processed_data)})")
                return False

            X = processed_data[self.features]
            y = processed_data['target']

            logging.info(f"[{self.symbol}] Entrenando modelo XGBoost con {len(processed_data)} muestras...")

            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=3,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                use_label_encoder=False,
                eval_metric='logloss',
                random_state=42
            )
            
            self.model.fit(X, y)
            logging.info(f"[{self.symbol}] Modelo entrenado con éxito.")
            return True
        except Exception as e:
            logging.error(f"[{self.symbol}] Error crítico durante el entrenamiento: {e}")
            self.model = None
            return False

    def predict(self, df):
        """Predice la dirección de la próxima vela (1: UP, 0: DOWN)."""
        if self.model is None:
            return None
        
        # Solo necesitamos la última fila para predecir el futuro inmediato
        processed_data = self.prepare_features(df)
        if processed_data.empty:
            return None
            
        last_features = processed_data[self.features].iloc[[-1]]
        prediction = self.model.predict(last_features)[0]
        probability = self.model.predict_proba(last_features)[0][1]
        
        return prediction, probability
