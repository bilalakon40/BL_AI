from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class AgentDecision:
    action: str
    confidence: float
    symbol: str
    qty: float
    order_type: str
    price: Optional[float] = None
    reasoning: str = ''
    strategy: str = ''
    metadata: Dict = field(default_factory=dict)


class BaseTradingAgent(ABC):
    def __init__(self, agent_id: str, strategy: str):
        self.agent_id = agent_id
        self.strategy = strategy
        self.is_active = False
        self.performance = {
            'trades': 0, 'wins': 0, 'total_pnl': 0.0, 'win_rate': 0.0,
        }

    @abstractmethod
    async def analyze(self, market_data: Dict, portfolio_state: Dict) -> AgentDecision:
        pass

    @abstractmethod
    async def train(self, historical_data: List[Dict]):
        pass

    def on_order_executed(self, decision: 'AgentDecision', result: dict):
        pass

    def update_performance(self, pnl: float):
        self.performance['trades'] += 1
        self.performance['total_pnl'] += pnl
        if pnl > 0:
            self.performance['wins'] += 1
        self.performance['win_rate'] = (
            self.performance['wins'] / self.performance['trades']
            if self.performance['trades'] > 0 else 0.0
        )
