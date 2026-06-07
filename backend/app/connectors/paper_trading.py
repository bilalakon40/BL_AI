import asyncio
import random
from typing import Dict, List, Optional, Callable
from datetime import datetime
from .base_exchange import BaseExchangeConnector


class PaperTradingConnector(BaseExchangeConnector):
    def __init__(self, initial_balance: float = 10000.0):
        self.exchange = None
        self.is_testnet = True
        self.balance = {'USDT': {'free': initial_balance, 'used': 0, 'total': initial_balance}}
        self.holdings: Dict[str, float] = {}
        self.orders: List[Dict] = []
        self.trades: List[Dict] = []
        self.current_prices: Dict[str, float] = {
            'BTCUSDT': 50000.0, 'ETHUSDT': 3000.0, 'SOLUSDT': 100.0, 'XRPUSDT': 0.5,
        }
        self.subscribers: List[Callable] = []

    async def initialize(self, api_key: str = '', api_secret: str = '', testnet: bool = True) -> bool:
        self.is_testnet = testnet
        return True

    async def get_balance(self, asset: str = 'USDT') -> Dict:
        data = self.balance.get(asset, {'free': 0, 'used': 0, 'total': 0})
        return {'asset': asset, **data}

    async def place_order(self, symbol: str, side: str, qty: float,
                         order_type: str = 'MARKET', price: Optional[float] = None) -> Dict:
        current_price = price or self.current_prices.get(symbol, 100.0)
        base_asset = symbol.replace('USDT', '')
        total_cost = qty * current_price

        if side.upper() == 'BUY':
            usdt_free = self.balance['USDT']['free']
            if total_cost > usdt_free:
                return {'status': 'rejected', 'reason': 'insufficient balance'}
            self.balance['USDT']['free'] -= total_cost
            self.holdings[base_asset] = self.holdings.get(base_asset, 0) + qty
        elif side.upper() == 'SELL':
            held = self.holdings.get(base_asset, 0)
            if qty > held:
                return {'status': 'rejected', 'reason': 'insufficient holdings'}
            self.holdings[base_asset] = held - qty
            self.balance['USDT']['free'] += total_cost

        order_id = f'paper_{datetime.now().timestamp()}'
        trade = {
            'order_id': order_id,
            'status': 'filled',
            'symbol': symbol,
            'side': side,
            'qty': qty,
            'price': current_price,
            'fee': {'cost': total_cost * 0.001, 'currency': 'USDT'},
            'timestamp': datetime.now().timestamp(),
        }
        self.trades.append(trade)
        return trade

    async def cancel_all_orders(self, symbol: str) -> bool:
        self.orders = [o for o in self.orders if o.get('symbol') != symbol]
        return True

    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        positions = []
        for asset, qty in self.holdings.items():
            if qty > 0:
                sym = f'{asset}USDT'
                if symbol and sym != symbol:
                    continue
                positions.append({'symbol': sym, 'amount': qty, 'free': qty})
        return positions

    async def subscribe_ticker(self, symbols: List[str], callback):
        while True:
            for symbol in symbols:
                base = self.current_prices.get(symbol, 100.0)
                change = base * random.uniform(-0.002, 0.002)
                new_price = base + change
                self.current_prices[symbol] = new_price
                ticker = {
                    'symbol': symbol,
                    'last': new_price,
                    'bid': new_price * 0.999,
                    'ask': new_price * 1.001,
                    'baseVolume': random.uniform(1000, 10000),
                    'timestamp': datetime.now().timestamp(),
                }
                await callback(symbol, ticker)
            await asyncio.sleep(2)

    async def close(self):
        pass
