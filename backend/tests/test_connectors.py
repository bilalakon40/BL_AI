import asyncio
import pytest
from app.connectors.paper_trading import PaperTradingConnector


def _run(coro):
    return asyncio.run(coro)


def test_paper_trading_initialize():
    conn = PaperTradingConnector(initial_balance=10000)
    result = _run(conn.initialize())
    assert result == True


def test_paper_trading_balance():
    conn = PaperTradingConnector(initial_balance=10000)
    _run(conn.initialize())
    balance = _run(conn.get_balance('USDT'))
    assert balance['free'] == 10000
    assert balance['total'] == 10000


def test_paper_trading_buy():
    conn = PaperTradingConnector(initial_balance=10000)
    _run(conn.initialize())
    order = _run(conn.place_order('BTCUSDT', 'BUY', 0.01, 'MARKET', 50000))
    assert order['status'] == 'filled'
    assert order['side'] == 'BUY'
    balance = _run(conn.get_balance('USDT'))
    assert balance['free'] < 10000


def test_paper_trading_sell():
    conn = PaperTradingConnector(initial_balance=10000)
    _run(conn.initialize())
    _run(conn.place_order('BTCUSDT', 'BUY', 0.01, 'MARKET', 50000))
    order = _run(conn.place_order('BTCUSDT', 'SELL', 0.01, 'MARKET', 51000))
    assert order['status'] == 'filled'
    assert order['side'] == 'SELL'


def test_insufficient_balance():
    conn = PaperTradingConnector(initial_balance=100)
    _run(conn.initialize())
    order = _run(conn.place_order('BTCUSDT', 'BUY', 10, 'MARKET', 50000))
    assert order['status'] == 'rejected'
    assert 'insufficient balance' in order['reason']


def test_cancel_all_orders():
    conn = PaperTradingConnector(initial_balance=10000)
    _run(conn.initialize())
    result = _run(conn.cancel_all_orders('BTCUSDT'))
    assert result == True


def test_get_positions():
    conn = PaperTradingConnector(initial_balance=10000)
    _run(conn.initialize())
    _run(conn.place_order('BTCUSDT', 'BUY', 0.01, 'MARKET', 50000))
    positions = _run(conn.get_positions())
    assert len(positions) > 0
    assert positions[0]['symbol'] == 'BTCUSDT'
