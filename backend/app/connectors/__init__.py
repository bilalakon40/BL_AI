from .base_exchange import BaseExchangeConnector
from .paper_trading import PaperTradingConnector


def BybitConnector(*args, **kwargs):
    from .bybit_connector import BybitConnector as _cls
    return _cls(*args, **kwargs)


def BinanceConnector(*args, **kwargs):
    from .binance_connector import BinanceConnector as _cls
    return _cls(*args, **kwargs)
