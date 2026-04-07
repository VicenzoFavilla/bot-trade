import ccxt
import os
import logging

class ExchangeHandler:
    def __init__(self, exchange_id='binance', api_key=None, api_secret=None, testnet=True):
        """
        Inicializa el manejador del exchange.
        """
        self.exchange_id = exchange_id
        exchange_class = getattr(ccxt, exchange_id)
        params = {
            'enableRateLimit': True,
        }
        
        # Solo agregar llaves si no son las de ejemplo o están vacías
        if api_key and "TU_API_KEY" not in api_key:
            params['apiKey'] = api_key
        if api_secret and "TU_SECRET" not in api_secret:
            params['secret'] = api_secret
            
        self.exchange = exchange_class(params)
        
        if testnet:
            self.exchange.set_sandbox_mode(True)
            logging.info(f"Modo Sandbox (Testnet) activado para {exchange_id}")

    def fetch_balance(self):
        """
        Obtiene el saldo de la cuenta.
        """
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            logging.error(f"Error al obtener el saldo: {e}")
            return None

    def fetch_ticker(self, symbol):
        """
        Obtiene el precio actual de un par (ej. 'BTC/USDT').
        """
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            logging.error(f"Error al obtener el ticker para {symbol}: {e}")
            return None

    def create_market_order(self, symbol, side, amount):
        """
        Crea una orden de mercado (compra o venta).
        """
        try:
            order = self.exchange.create_market_order(symbol, side, amount)
            logging.info(f"Orden de mercado {side} creada: {amount} {symbol}")
            return order
        except Exception as e:
            logging.error(f"Error al crear orden de mercado: {e}")
            return None

    def create_limit_order(self, symbol, side, amount, price):
        """
        Crea una orden límite.
        """
        try:
            order = self.exchange.create_limit_order(symbol, side, amount, price)
            logging.info(f"Orden límite {side} creada: {amount} {symbol} a {price}")
            return order
        except Exception as e:
            logging.error(f"Error al crear orden límite: {e}")
            return None
