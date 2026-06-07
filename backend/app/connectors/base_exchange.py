from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseExchangeConnector(ABC):

    @abstractmethod
    async def initialize(self, api_key: str, api_secret: str, testnet: bool = True) -> bool:
        pass

    @abstractmethod
    async def get_balance(self, asset: str = 'USDT') -> Dict:
        pass

    @abstractmethod
    async def place_order(self, symbol: str, side: str, qty: float,
                         order_type: str = 'MARKET', price: Optional[float] = None) -> Dict:
        pass

    @abstractmethod
    async def cancel_all_orders(self, symbol: str) -> bool:
        pass

    @abstractmethod
    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        pass

    @abstractmethod
    async def subscribe_ticker(self, symbols: List[str], callback):
        pass

    @abstractmethod
    async def close(self):
        pass
