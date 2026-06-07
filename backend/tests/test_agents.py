import asyncio
import pytest
from app.agents.grid_agent import GridTradingAgent
from app.agents.trend_agent import TrendFollowingAgent
from app.agents.base_agent import AgentDecision


def _run(coro):
    return asyncio.run(coro)


def test_grid_agent_hold():
    agent = GridTradingAgent('test_grid', 'BTCUSDT', {'upper_price': 55000, 'lower_price': 45000, 'grid_count': 10})
    decision = _run(agent.analyze({'price': 45000}, {'balance': 1000}))
    assert decision.action == 'HOLD'


def test_grid_agent_buy():
    agent = GridTradingAgent('test_grid', 'BTCUSDT', {'upper_price': 55000, 'lower_price': 45000, 'grid_count': 10})
    decision = _run(agent.analyze({'price': 55000}, {'balance': 1000}))
    assert decision.action == 'BUY'
    assert decision.order_type == 'LIMIT'


def test_grid_agent_calculate_grids():
    agent = GridTradingAgent('test_grid', 'BTCUSDT', {'upper_price': 100, 'lower_price': 0, 'grid_count': 4})
    assert len(agent.grids) == 5
    assert agent.grids[0] == 0
    assert agent.grids[4] == 100


def test_trend_agent_hold_insufficient_data():
    agent = TrendFollowingAgent('test_trend', 'ETHUSDT', fast_period=9, slow_period=21)
    decision = _run(agent.analyze({'price': 3000}, {'balance': 10000, 'holdings': {}}))
    assert decision.action == 'HOLD'
    assert 'Building price history' in decision.reasoning


def test_agent_performance_update():
    agent = TrendFollowingAgent('test_perf', 'ETHUSDT')
    agent.update_performance(100)
    assert agent.performance['trades'] == 1
    assert agent.performance['wins'] == 1
    assert agent.performance['total_pnl'] == 100
    assert agent.performance['win_rate'] == 1.0

    agent.update_performance(-50)
    assert agent.performance['trades'] == 2
    assert agent.performance['wins'] == 1
    assert agent.performance['total_pnl'] == 50
    assert agent.performance['win_rate'] == 0.5


def test_agent_decision_dataclass():
    d = AgentDecision(action='BUY', confidence=0.8, symbol='BTCUSDT', qty=0.01, order_type='MARKET', reasoning='test', strategy='grid')
    assert d.action == 'BUY'
    assert d.confidence == 0.8
    assert d.symbol == 'BTCUSDT'


def test_trend_agent_signals():
    agent = TrendFollowingAgent('test_trend', 'ETHUSDT', fast_period=5, slow_period=10)
    for i in range(15):
        decision = _run(agent.analyze({'price': float(100 + i * 10)}, {'balance': 10000, 'holdings': {}}))
    assert decision.action in ('BUY', 'HOLD')
