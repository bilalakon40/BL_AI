from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, date


@dataclass
class Agent:
    agent_id: str
    strategy: str
    is_active: bool = False
    config: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


@dataclass
class Trade:
    time: datetime
    trade_id: str
    agent_id: str
    symbol: str
    side: str
    qty: float
    price: float
    order_type: str
    fee: Optional[float] = None
    pnl: Optional[float] = None
    status: str = "pending"
    exchange: str = ""
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DecisionLog:
    agent_id: str
    symbol: str
    action: str
    confidence: float
    reasoning: str
    risk_check_passed: bool
    executed: bool = False
    execution_result: Optional[Dict[str, Any]] = None


@dataclass
class DailyStats:
    date: date
    starting_balance: float
    ending_balance: float
    total_trades: int = 0
    winning_trades: int = 0
    total_fees: float = 0.0
    max_drawdown_pct: float = 0.0
