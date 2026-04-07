import time
import logging
import pandas as pd
import sys
import os

# Añadir el directorio raíz al path para importar la configuración
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchange_handler import ExchangeHandler
from strategy import MeanReversionStrategy
from config.config import CONFIG

# Configuración básica de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Cargar parámetros desde el archivo de configuración
    SYMBOL = CONFIG['trading']['symbol']
    TIMEFRAME = CONFIG['trading']['timeframe']
    MEAN_WINDOW = CONFIG['strategy']['mean_window']
    THRESHOLD = CONFIG['strategy']['threshold']
    
    # Parámetros del exchange
    EXCHANGE_ID = CONFIG['exchange']['id']
    API_KEY = CONFIG['exchange']['apiKey']
    API_SECRET = CONFIG['exchange']['secret']
    TESTNET = CONFIG['exchange']['testnet']
    
    # Inicializar exchange y estrategia
    handler = ExchangeHandler(
        exchange_id=EXCHANGE_ID, 
        api_key=API_KEY, 
        api_secret=API_SECRET, 
        testnet=TESTNET
    )
    strategy = MeanReversionStrategy(window=MEAN_WINDOW, threshold=THRESHOLD)
    
    logging.info(f"Iniciando bot para {SYMBOL} con estrategia {strategy.name}")
    
    while True:
        try:
            # 1. Obtener datos históricos de velas (OHLCV)
            # Limitamos a 100 velas para tener suficiente margen para las medias móviles
            ohlcv = handler.exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # 2. Generar señal de trading
            signal = strategy.generate_signals(df)
            logging.info(f"Señal actual: {signal}")
            
            # 3. Ejecutar acción basada en la señal
            if signal == 'buy':
                logging.info(f"EJECUTANDO COMPRA para {SYMBOL}")
                # handler.create_market_order(SYMBOL, 'buy', 0.001) # Descomentar para activar
            elif signal == 'sell':
                logging.info(f"EJECUTANDO VENTA para {SYMBOL}")
                # handler.create_market_order(SYMBOL, 'sell', 0.001) # Descomentar para activar
            
            # 4. Esperar al siguiente intervalo
            time.sleep(60) # Esperar 1 minuto
            
        except Exception as e:
            logging.error(f"Error en el bucle principal: {e}")
            time.sleep(10) # Reintentar después de un error

if __name__ == "__main__":
    main()
