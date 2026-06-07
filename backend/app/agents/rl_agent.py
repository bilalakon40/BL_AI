from typing import Dict, List, Optional
import json
import numpy as np
from .base_agent import BaseTradingAgent, AgentDecision
from app.config import settings


class OllamaAgent(BaseTradingAgent):
    def __init__(self, agent_id: str, symbol: str,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None):
        super().__init__(agent_id, 'ollama_llm')
        self.symbol = symbol
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        from openai import OpenAI
        self.client = OpenAI(base_url=f'{self.base_url}/v1', api_key='ollama')
        self.price_history: List[float] = []

    def _build_market_context(self, market_data: Dict, portfolio_state: Dict) -> str:
        self.price_history.append(market_data.get('price', 0))
        if len(self.price_history) > 20:
            self.price_history.pop(0)

        prices = np.array(self.price_history)
        sma_short = float(np.mean(prices[-5:])) if len(prices) >= 5 else 0
        sma_long = float(np.mean(prices)) if len(prices) > 0 else 0
        trend = 'up' if sma_short > sma_long else 'down'

        return json.dumps({
            'symbol': self.symbol,
            'current_price': market_data.get('price', 0),
            'bid': market_data.get('bid', 0),
            'ask': market_data.get('ask', 0),
            'volume_24h': market_data.get('volume', 0),
            'price_change_24h_pct': market_data.get('24h_change', 0),
            'short_trend': trend,
            'sma_short': round(sma_short, 2),
            'sma_long': round(sma_long, 2),
            'portfolio_balance_usdt': round(portfolio_state.get('balance', 0), 2),
            'open_positions': portfolio_state.get('open_positions', 0),
            'holdings': portfolio_state.get('holdings', {}).get(self.symbol, 0),
            'win_rate': round(self.performance.get('win_rate', 0), 2),
            'total_trades': self.performance.get('trades', 0),
        })

    async def analyze(self, market_data: Dict, portfolio_state: Dict) -> AgentDecision:
        context = self._build_market_context(market_data, portfolio_state)

        prompt = (
            f"You are a spot trading advisor for {self.symbol}. "
            "Based on the current market data below, decide: BUY, SELL, or HOLD. "
            "Reply with ONLY valid JSON: {\"action\":\"BUY|SELL|HOLD\",\"confidence\":0.0-1.0,\"reasoning\":\"...\"}\n\n"
            f"Market data:\n{context}"
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3,
                max_tokens=150,
            )
            content = resp.choices[0].message.content.strip()
            content = content.removeprefix('```json').removeprefix('```').removesuffix('```').strip()
            result = json.loads(content)
        except Exception as e:
            return AgentDecision(
                action='HOLD', confidence=0.5, symbol=self.symbol,
                qty=0, order_type='MARKET', price=None,
                reasoning=f'Ollama error: {e}', strategy='ollama_llm',
            )

        action = result.get('action', 'HOLD').upper()
        confidence = float(result.get('confidence', 0.5))
        reasoning = result.get('reasoning', 'No reasoning provided')

        if action not in ('BUY', 'SELL', 'HOLD'):
            action = 'HOLD'
            confidence = 0.5

        qty = 0
        if action == 'BUY' and confidence > 0.5:
            qty = portfolio_state.get('balance', 0) * 0.15 / max(market_data.get('price', 1), 0.01)
        elif action == 'SELL' and confidence > 0.5:
            qty = portfolio_state.get('holdings', {}).get(self.symbol, 0)

        return AgentDecision(
            action=action, confidence=confidence, symbol=self.symbol,
            qty=qty, order_type='MARKET' if qty > 0 else 'MARKET',
            price=None, reasoning=reasoning, strategy='ollama_llm',
        )

    async def train(self, historical_data: List[Dict]):
        pass
