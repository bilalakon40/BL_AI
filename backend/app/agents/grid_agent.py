from typing import Dict, List
from .base_agent import BaseTradingAgent, AgentDecision


class GridTradingAgent(BaseTradingAgent):
    def __init__(self, agent_id: str, symbol: str, config: Dict):
        super().__init__(agent_id, 'grid')
        self.symbol = symbol
        self.upper_price = config['upper_price']
        self.lower_price = config['lower_price']
        self.grid_count = config.get('grid_count', 10)
        self.grids = self._calculate_grids()
        self.active_orders: Dict[float, str] = {}
        self.holdings = 0.0

    def _calculate_grids(self) -> List[float]:
        step = (self.upper_price - self.lower_price) / self.grid_count
        return [self.lower_price + (step * i) for i in range(self.grid_count + 1)]

    async def analyze(self, market_data: Dict, portfolio_state: Dict) -> AgentDecision:
        current_price = market_data.get('price', 0)
        balance = portfolio_state.get('balance', 0)

        buy_candidates = [
            g for g in self.grids
            if g < current_price and g not in self.active_orders
        ]
        sell_candidates = [
            g for g in self.grids
            if g > current_price and g in self.active_orders
        ]

        if buy_candidates and balance > 10:
            target = max(buy_candidates)
            qty = (balance * 0.1) / target
            self.active_orders[target] = 'pending'
            return AgentDecision(
                action='BUY', confidence=0.8, symbol=self.symbol,
                qty=qty, order_type='LIMIT', price=target,
                reasoning=f'Grid buy at level {target:.2f}', strategy='grid',
            )

        if sell_candidates and self.holdings > 0:
            target = min(sell_candidates)
            qty = self.holdings / max(len(sell_candidates), 1)
            self.active_orders[target] = 'pending'
            return AgentDecision(
                action='SELL', confidence=0.8, symbol=self.symbol,
                qty=qty, order_type='LIMIT', price=target,
                reasoning=f'Grid sell at level {target:.2f}', strategy='grid',
            )

        return AgentDecision(
            action='HOLD', confidence=0.5, symbol=self.symbol,
            qty=0, order_type='MARKET', price=None,
            reasoning='No grid level triggered', strategy='grid',
        )

    def on_order_executed(self, decision: 'AgentDecision', result: dict):
        price = decision.price or result.get('price', 0)
        qty = result.get('qty', decision.qty)
        if decision.action == 'BUY' and price in self.active_orders:
            del self.active_orders[price]
            self.holdings += qty
        elif decision.action == 'SELL' and price in self.active_orders:
            del self.active_orders[price]
            self.holdings = max(0, self.holdings - qty)

    async def train(self, historical_data: List[Dict]):
        pass
