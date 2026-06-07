import asyncio
from typing import List, Dict, Callable, Any
from app.risk.engine import RiskEngine
from app.connectors.base_exchange import BaseExchangeConnector
from app.agents.base_agent import BaseTradingAgent
from app.core.order_manager import OrderManager


class TradingOrchestrator:
    def __init__(self, exchange_connector: BaseExchangeConnector,
                 risk_engine: RiskEngine, agents: List[BaseTradingAgent]):
        self.exchange = exchange_connector
        self.risk = risk_engine
        self.agents = agents
        self.order_manager = OrderManager(exchange_connector)
        self.is_running = False
        self.market_cache: Dict[str, Dict] = {}
        self._alert_handlers: List[Callable] = []

    def on_alert(self, handler: Callable):
        self._alert_handlers.append(handler)

    async def _emit(self, channel: str, data: Any):
        for handler in self._alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(channel, data)
                else:
                    handler(channel, data)
            except Exception:
                pass

    async def start(self, symbols: List[str], interval_seconds: int = 60):
        self.is_running = True

        try:
            if hasattr(self.exchange, 'subscribe_ticker'):
                asyncio.create_task(self.exchange.subscribe_ticker(symbols, self._on_price_update))
        except Exception:
            pass

        while self.is_running:
            try:
                await self._trading_cycle(symbols)
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                await asyncio.sleep(5)

    async def _trading_cycle(self, symbols: List[str]):
        balance = await self.exchange.get_balance('USDT')
        positions = []
        for sym in symbols:
            pos = await self.exchange.get_positions(sym)
            positions.extend(pos)

        portfolio = {
            'balance': balance['free'],
            'total_balance': balance['total'],
            'open_positions': len(positions),
            'position_value': sum(
                p.get('amount', 0) * self.market_cache.get(p.get('symbol', ''), {}).get('price', 0)
                for p in positions
            ),
            'holdings': {p['symbol']: p['amount'] for p in positions if p.get('amount', 0) > 0},
        }

        decisions = []
        for agent in self.agents:
            if not agent.is_active:
                continue
            for symbol in symbols:
                if symbol not in self.market_cache:
                    continue
                decision = await agent.analyze(self.market_cache[symbol], portfolio)
                if decision.action != 'HOLD':
                    decisions.append(decision)

        for dec in decisions:
            order_value = dec.qty * (dec.price or self.market_cache.get(dec.symbol, {}).get('price', 0))
            allowed, reason = self.risk.pre_trade_check(
                portfolio['balance'], portfolio['open_positions'], order_value, dec.symbol, dec.order_type,
            )
            if not allowed:
                await self._emit('alerts', f'Risk blocked: {dec.strategy} {dec.action} {dec.symbol} - {reason}')
                continue

            try:
                result = await self.exchange.place_order(
                    symbol=dec.symbol, side=dec.action, qty=dec.qty,
                    order_type=dec.order_type, price=dec.price,
                )
                if result.get('status') in ('filled', 'closed'):
                    agent.on_order_executed(dec, result)
                await self.order_manager.track_order(result, dec.strategy)
                await self._emit('trades', str(result))
            except Exception as e:
                await self._emit('alerts', f'Execution failed: {dec.action} {dec.symbol} - {e}')

        await self._emit('state', self.get_state())

    async def _on_price_update(self, symbol: str, ticker: Dict):
        self.market_cache[symbol] = {
            'price': ticker.get('last', 0),
            'bid': ticker.get('bid', 0),
            'ask': ticker.get('ask', 0),
            'volume': ticker.get('baseVolume', 0),
            'timestamp': ticker.get('timestamp', 0),
            'bid_ask_spread': ticker.get('ask', 0) - ticker.get('bid', 0) if ticker.get('bid') and ticker.get('ask') else 0,
            '24h_change': ticker.get('percentage', 0),
        }
        await self._emit('prices', {symbol: self.market_cache[symbol]})

    async def emergency_stop(self):
        self.is_running = False
        for agent in self.agents:
            agent.is_active = False
        for symbol in list(self.market_cache.keys()):
            try:
                await self.exchange.cancel_all_orders(symbol)
            except Exception:
                pass
        await self._emit('alerts', 'EMERGENCY STOP ACTIVATED')

    async def get_state(self) -> Dict:
        active_agents = [a for a in self.agents if a.is_active]
        return {
            'is_running': self.is_running,
            'is_locked': self.risk.is_locked,
            'lock_reason': self.risk.lock_reason,
            'active_agents': len(active_agents),
            'total_agents': len(self.agents),
            'market_symbols': list(self.market_cache.keys()),
            'daily_stats': self.risk.daily_stats,
        }
