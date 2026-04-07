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

def analyze_market_and_recommend(handler, timeframe, window):
    cryptos = ['BTC/ARS', 'ETH/ARS', 'SOL/ARS']
    print("\n" + "="*50)
    print("📊 ANALIZANDO EL MERCADO PARA RECOMENDACIONES...")
    print("="*50)
    
    recommendation = None
    max_distance = -1
    
    analysis_results = []
    
    for symbol in cryptos:
        try:
            ohlcv = handler.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=window+1)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            if len(df) >= window:
                sma = df['close'].rolling(window=window).mean().iloc[-1]
                current_price = df['close'].iloc[-1]
                distance = abs(current_price - sma) / sma
                
                analysis_results.append({
                    'symbol': symbol,
                    'price': current_price,
                    'sma': sma,
                    'distance_pct': distance * 100
                })
                
                if distance > max_distance:
                    max_distance = distance
                    recommendation = symbol
                    
        except Exception as e:
            logging.error(f"Error analizando {symbol}: {e}")
            
    for res in analysis_results:
        print(f"🔸 [{res['symbol']}] Precio: {res['price']:.2f} | SMA({window}): {res['sma']:.2f} | Dist. a media: {res['distance_pct']:.2f}%")
        
    print("-" * 50)
    if recommendation:
        print(f"💡 RECOMENDACIÓN: {recommendation} está más alejado de su media móvil.")
        print("   Ofrece una mayor probabilidad de acercarse al umbral de cruce (Mean Reversion).")
    else:
        print("💡 RECOMENDACIÓN: No se pudo determinar.")
    print("="*50 + "\n")

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
    
    # Inicializar exchange
    handler = ExchangeHandler(
        exchange_id=EXCHANGE_ID, 
        api_key=API_KEY, 
        api_secret=API_SECRET, 
        testnet=TESTNET
    )
    
    # 1. Analizar el mercado y recomendar
    analyze_market_and_recommend(handler, TIMEFRAME, MEAN_WINDOW)
    
    # 2. Definir lista de símbolos a operar
    # Si la config no tiene 'symbols', usamos la lista por defecto
    SYMBOLS = CONFIG['trading'].get('symbols', ['BTC/ARS', 'ETH/ARS', 'SOL/ARS'])
    
    print(f"\n✅ Operando con: {', '.join(SYMBOLS)}. Inicializando bot...\n")
    
    # Inicializar estrategia
    strategy = MeanReversionStrategy(window=MEAN_WINDOW, threshold=THRESHOLD)
    
    logging.info(f"Iniciando bot multimoneda con estrategia {strategy.name}")
    
    while True:
        try:
            for symbol in SYMBOLS:
                # 1. Obtener datos históricos de velas (OHLCV)
                ohlcv = handler.exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=100)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # 2. Generar señal de trading
                signal = strategy.generate_signals(df)
                current_price = float(df['close'].iloc[-1])
                logging.info(f"[{symbol}] Señal: {signal} | Precio: {current_price}")
                
                # 3. Ejecutar acción basada en la señal
                if signal == 'buy':
                    quote_currency = symbol.split('/')[1]
                    balance = handler.fetch_balance()
                    
                    if balance and quote_currency in balance:
                        available_quote = float(balance[quote_currency]['free'])
                        # Para multimoneda, usamos una fracción del saldo total disponible
                        # Dividimos el saldo entre la cantidad de monedas para no agotar todo en una de ellas
                        amount_to_spend = (available_quote / len(SYMBOLS)) * 0.95
                        
                        if amount_to_spend > 1.0: 
                            amount_to_buy = round(amount_to_spend / current_price, 6)
                            logging.info(f"EJECUTANDO COMPRA de {amount_to_buy} {symbol} usando ~{amount_to_spend} {quote_currency}")
                            handler.create_market_order(symbol, 'buy', amount_to_buy)
                        else:
                            logging.warning(f"Saldo insuficiente de {quote_currency} para {symbol}: tienes {available_quote}. Se necesita más.")
                    
                elif signal == 'sell':
                    base_currency = symbol.split('/')[0]
                    balance = handler.fetch_balance()
                    
                    if balance and base_currency in balance:
                        available_balance = float(balance[base_currency]['free'])
                        if available_balance * current_price > 5.0: 
                            amount_to_sell = round(available_balance * 0.999, 6)
                            logging.info(f"EJECUTANDO VENTA de {amount_to_sell} {base_currency}")
                            handler.create_market_order(symbol, 'sell', amount_to_sell)
                        else:
                            logging.warning(f"[{symbol}] Señal de VENTA: Tienes {available_balance} {base_currency}, valor insuficiente para vender.")
            
            # 4. Esperar al siguiente intervalo
            logging.info("Ciclo completado. Esperando 1 minuto...")
            time.sleep(60)
            
        except Exception as e:
            logging.error(f"Error en el bucle principal: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
