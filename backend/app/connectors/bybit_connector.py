import ccxt.pro as ccxt
import asyncio
from typing import Dict, List, Optional
from .base_exchange import BaseExchangeConnector


class BybitConnector(BaseExchangeConnector):
    def __init__(self):
        self.exchange: Optional[ccxt.Exchange] = None
        self.is_testnet = True

    async def initialize(self, api_key: str, api_secret: str, testnet: bool = True) -> bool:
        config = {
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'},
        }
        if testnet:
            config['sandbox'] = True

        self.exchange = ccxt.bybit(config)
        self.is_testnet = testnet

        try:
            await self.exchange.fetch_balance()
            return True
        except Exception as e:
            raise ConnectionError(f'Bybit connection failed: {e}')

    async def get_balance(self, asset: str = 'USDT') -> Dict:
        balance = await self.exchange.fetch_balance()
        asset_data = balance.get(asset, {})
        return {
            'asset': asset,
            'free': float(asset_data.get('free', 0)),
            'used': float(asset_data.get('used', 0)),
            'total': float(asset_data.get('total', 0)),
        }

    async def place_order(self, symbol: str, side: str, qty: float,
                         order_type: str = 'MARKET', price: Optional[float] = None) -> Dict:
        params = {}
        if order_type == 'LIMIT':
            params['price'] = price
            params['timeInForce'] = 'GTC'

        order = await self.exchange.create_order(
            symbol=symbol,
            type=order_type.lower(),
            side=side.lower(),
            amount=qty,
            params=params,
        )
        return {
            'order_id': order['id'],
            'status': order['status'],
            'symbol': order['symbol'],
            'side': order['side'],
            'qty': order['amount'],
            'price': order.get('average', order.get('price')),
            'fee': order.get('fee', {}),
            'timestamp': order['timestamp'],
        }

    async def cancel_all_orders(self, symbol: str) -> bool:
        try:
            await self.exchange.cancel_all_orders(symbol)
            return True
        except Exception:
            return False

    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        try:
            balance = await self.exchange.fetch_balance()
            positions = []
            for asset, data in balance.items():
                if isinstance(data, dict) and data.get('total', 0) > 0:
                    if symbol and asset != symbol.replace('USDT', ''):
                        continue
                    sym = asset if asset.endswith('USDT') else f'{asset}USDT'
                    positions.append({
                        'symbol': sym,
                        'amount': float(data.get('total', 0)),
                        'free': float(data.get('free', 0)),
                    })
            return positions
        except Exception:
            return []

    async def subscribe_ticker(self, symbols: List[str], callback):
        while True:
            try:
                for symbol in symbols:
                    ticker = await self.exchange.watch_ticker(symbol)
                    await callback(symbol, ticker)
            except Exception as e:
                await asyncio.sleep(5)

    async def close(self):
        if self.exchange:
            await self.exchange.close()
