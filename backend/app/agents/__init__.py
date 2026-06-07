from .base_agent import BaseTradingAgent, AgentDecision
from .grid_agent import GridTradingAgent
from .trend_agent import TrendFollowingAgent


def OllamaAgent(*args, **kwargs):
    from .rl_agent import OllamaAgent as _OllamaAgent
    return _OllamaAgent(*args, **kwargs)
