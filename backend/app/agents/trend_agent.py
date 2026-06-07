from typing import Dict, List
import numpy as np
from .base_agent import BaseTradingAgent, AgentDecision


def _ema(data: List[float], period: int) -> float:
    if len(data) < period:
        return data[-1] if data else 0
    alpha = 2 / (period + 1)
    ema = data[0]
    for price in data[1:]:
        ema = price * alpha + ema * (1 - alpha)
    return ema


def _rsi(data: List[float], period: int = 14) -> float:
    if len(data) < period + 1:
        return 50.0
    deltas = np.diff(data[-period - 1:])
    gains = deltas[deltas > 0].sum() / period
    losses = -deltas[deltas < 0].sum() / period
    if losses == 0:
        return 100.0
    rs = gains / losses
    return 100 - (100 / (1 + rs))


def _macd(data: List[float]) -> tuple:
    fast = _ema(data, 12)
    slow = _ema(data, 26)
    macd_line = fast - slow
    signal = _ema([macd_line] * min(len(data), 9), 9) if len(data) >= 9 else macd_line
    return macd_line, signal


def _bollinger(data: List[float], period: int = 20) -> tuple:
    if len(data) < period:
        return data[-1] * 1.1, data[-1] * 0.9
    recent = data[-period:]
    mean = np.mean(recent)
    std = np.std(recent)
    return mean + 2 * std, mean - 2 * std


class TrendFollowingAgent(BaseTradingAgent):
    def __init__(self, agent_id: str, symbol: str,
                 fast_period: int = 9, slow_period: int = 21):
        super().__init__(agent_id, 'ema_crossover')
        self.symbol = symbol
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.price_history: List[float] = []
        self.volume_history: List[float] = []

    async def analyze(self, market_data: Dict, portfolio_state: Dict) -> AgentDecision:
        current_price = market_data.get('price', 0)
        current_volume = market_data.get('volume', 0)

        self.price_history.append(current_price)
        self.volume_history.append(current_volume)
        if len(self.price_history) > self.slow_period * 3:
            self.price_history.pop(0)
            self.volume_history.pop(0)

        if len(self.price_history) < self.slow_period + 1:
            return AgentDecision(
                action='HOLD', confidence=0.5, symbol=self.symbol,
                qty=0, order_type='MARKET', price=None,
                reasoning='Building price history', strategy='ema_crossover',
            )

        fast_ema = _ema(self.price_history, self.fast_period)
        slow_ema = _ema(self.price_history, self.slow_period)
        prev_fast = _ema(self.price_history[:-1], self.fast_period)
        prev_slow = _ema(self.price_history[:-1], self.slow_period)
        rsi = _rsi(self.price_history, 14)
        macd_line, macd_signal = _macd(self.price_history)
        bb_upper, bb_lower = _bollinger(self.price_history, 20)

        reasoning_parts = [
            f'EMA fast={fast_ema:.2f}', f'slow={slow_ema:.2f}',
            f'RSI={rsi:.1f}', f'MACD={macd_line:.2f}/{macd_signal:.2f}',
        ]

        buy_signals = 0
        sell_signals = 0

        if prev_fast <= prev_slow and fast_ema > slow_ema:
            buy_signals += 1
        if prev_fast >= prev_slow and fast_ema < slow_ema:
            sell_signals += 1
        if rsi < 30:
            buy_signals += 1
        elif rsi > 70:
            sell_signals += 1
        if macd_line > macd_signal:
            buy_signals += 1
        elif macd_line < macd_signal:
            sell_signals += 1
        if current_price <= bb_lower:
            buy_signals += 1
        elif current_price >= bb_upper:
            sell_signals += 1

        if buy_signals >= 2:
            qty = portfolio_state.get('balance', 0) * 0.2 / max(current_price, 0.01)
            return AgentDecision(
                action='BUY', confidence=min(0.5 + buy_signals * 0.1, 0.9),
                symbol=self.symbol, qty=qty, order_type='MARKET', price=None,
                reasoning='Signals: ' + ', '.join(reasoning_parts),
                strategy='ema_crossover',
            )
        elif sell_signals >= 2:
            qty = portfolio_state.get('holdings', {}).get(self.symbol, 0)
            if qty > 0:
                return AgentDecision(
                    action='SELL', confidence=min(0.5 + sell_signals * 0.1, 0.9),
                    symbol=self.symbol, qty=qty, order_type='MARKET', price=None,
                    reasoning='Signals: ' + ', '.join(reasoning_parts),
                    strategy='ema_crossover',
                )

        return AgentDecision(
            action='HOLD', confidence=0.5, symbol=self.symbol,
            qty=0, order_type='MARKET', price=None,
            reasoning='No clear signal: ' + ', '.join(reasoning_parts),
            strategy='ema_crossover',
        )

    async def train(self, historical_data: List[Dict]):
        pass
