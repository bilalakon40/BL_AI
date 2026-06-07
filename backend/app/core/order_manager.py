from typing import Dict, Optional
from datetime import datetime
from app.db.database import execute


class OrderManager:
    def __init__(self, exchange):
        self.exchange = exchange
        self.pending_orders: Dict[str, Dict] = {}

    async def track_order(self, order: Dict, agent_id: str):
        order_id = order.get('order_id')
        if order_id:
            self.pending_orders[order_id] = {
                'order': order,
                'agent_id': agent_id,
                'timestamp': datetime.now(),
                'status': order.get('status', 'pending'),
            }
        await self._log_decision(order, agent_id)

    async def check_fills(self, symbol: str, order_id: str) -> Optional[Dict]:
        try:
            order = await self.exchange.fetch_order(order_id, symbol)
            if order['status'] == 'closed':
                tracked = self.pending_orders.pop(order_id, {})
                filled_order = {
                    **tracked.get('order', {}),
                    'status': 'filled',
                    'filled_qty': order.get('filled', 0),
                    'average_price': order.get('average', order.get('price')),
                }
                await self._record_trade(filled_order, tracked.get('agent_id', ''))
                return filled_order
        except Exception:
            pass
        return None

    async def _log_decision(self, order: Dict, agent_id: str):
        import uuid
        execute(
            """INSERT INTO decision_logs (id, agent_id, symbol, action, confidence, reasoning, risk_check_passed, executed, execution_result)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), agent_id, order.get('symbol', ''), order.get('side', ''),
             0.0, 'Order placed via orchestrator', 1, 1, str(order)),
        )

    async def _record_trade(self, order: Dict, agent_id: str):
        import uuid
        execute(
            """INSERT INTO trades (time, trade_id, agent_id, symbol, side, qty, price, order_type, fee, pnl, status, exchange, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(), str(uuid.uuid4()), agent_id,
             order.get('symbol', ''), order.get('side', ''), order.get('qty', 0),
             order.get('price', 0), order.get('order_type', 'MARKET'),
             0, 0, 'filled', 'exchange', '{}'),
        )
