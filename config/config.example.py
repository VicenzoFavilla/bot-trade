# Configuración del Bot de Trading (Ejemplo)

# IMPORTANTE: No compartas tus claves API reales.
# Renombra este archivo a config.py y rellena tus claves.

CONFIG = {
    'exchange': {
        'id': 'binance',
        'apiKey': '', # Tu API Key de la Testnet
        'secret': '', # Tu API Secret de la Testnet
        'testnet': True,
    },
    'trading': {
        'symbol': 'BTC/USDT',
        'timeframe': '1m',
        'limit': 100, # Cantidad de velas para cálculos
        'amount': 0.001, # Cantidad a comprar/vender (en BTC)
    },
    'strategy': {
        'short_window': 10,
        'long_window': 50,
        'mean_window': 20,
        'threshold': 0.02,
    }
}
