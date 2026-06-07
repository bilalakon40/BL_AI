from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, date
from app.risk.engine import RiskEngine, RISK_PROFILE
from app.connectors.paper_trading import PaperTradingConnector
from app.agents.grid_agent import GridTradingAgent
from app.agents.trend_agent import TrendFollowingAgent
from app.agents.rl_agent import OllamaAgent
from app.core.orchestrator import TradingOrchestrator
from app.db.database import execute
from app.utils.logger import get_logger
from app.security.auth import require_auth

router = APIRouter()
logger = get_logger('routes')

orchestrator: Optional[TradingOrchestrator] = None
risk_engine = RiskEngine(RISK_PROFILE)


async def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        exchange = PaperTradingConnector(initial_balance=10000.0)
        await exchange.initialize()
        agents = [
            GridTradingAgent('grid_btc', 'BTCUSDT', {'upper_price': 55000, 'lower_price': 45000, 'grid_count': 10}),
            TrendFollowingAgent('trend_eth', 'ETHUSDT', fast_period=9, slow_period=21),
        ]
        orchestrator = TradingOrchestrator(exchange, risk_engine, agents)
    return orchestrator


class StartRequest(BaseModel):
    symbols: List[str] = ['BTCUSDT', 'ETHUSDT']
    interval: int = 60


class StopRequest(BaseModel):
    password: str


class UnlockRequest(BaseModel):
    password: str


class AgentConfig(BaseModel):
    agent_id: str
    strategy: str
    symbol: str
    config: Dict = {}


@router.post('/orchestrator/start')
async def start_orchestrator(req: StartRequest, auth: dict = Depends(require_auth)):
    orch = await get_orchestrator()
    if orch.is_running:
        raise HTTPException(400, 'Already running')
    import asyncio
    asyncio.create_task(orch.start(req.symbols, req.interval))
    return {'status': 'started', 'symbols': req.symbols}


@router.post('/orchestrator/stop')
async def stop_orchestrator(auth: dict = Depends(require_auth)):
    orch = await get_orchestrator()
    await orch.emergency_stop()
    return {'status': 'stopped', 'message': 'Emergency stop executed'}


@router.get('/orchestrator/state')
async def get_state():
    orch = await get_orchestrator()
    return await orch.get_state()


@router.post('/agents/create')
async def create_agent(cfg: AgentConfig, auth: dict = Depends(require_auth)):
    orch = await get_orchestrator()
    if cfg.strategy == 'grid':
        agent = GridTradingAgent(cfg.agent_id, cfg.symbol, cfg.config)
    elif cfg.strategy == 'trend':
        agent = TrendFollowingAgent(cfg.agent_id, cfg.symbol, **cfg.config)
    elif cfg.strategy == 'ollama':
        agent = OllamaAgent(cfg.agent_id, cfg.symbol,
                           base_url=cfg.config.get('base_url'),
                           model=cfg.config.get('model'))
    else:
        raise HTTPException(400, f'Unknown strategy: {cfg.strategy}')
    orch.agents.append(agent)
    return {'status': 'created', 'agent_id': cfg.agent_id}


@router.post('/agents/{agent_id}/start')
async def start_agent(agent_id: str, auth: dict = Depends(require_auth)):
    orch = await get_orchestrator()
    for agent in orch.agents:
        if agent.agent_id == agent_id:
            agent.is_active = True
            return {'status': 'started', 'agent_id': agent_id}
    raise HTTPException(404, f'Agent {agent_id} not found')


@router.post('/agents/{agent_id}/stop')
async def stop_agent(agent_id: str, auth: dict = Depends(require_auth)):
    orch = await get_orchestrator()
    for agent in orch.agents:
        if agent.agent_id == agent_id:
            agent.is_active = False
            return {'status': 'stopped', 'agent_id': agent_id}
    raise HTTPException(404, f'Agent {agent_id} not found')


@router.get('/agents')
async def list_agents():
    orch = await get_orchestrator()
    return [
        {
            'agent_id': a.agent_id,
            'strategy': a.strategy,
            'is_active': a.is_active,
            'performance': a.performance,
        }
        for a in orch.agents
    ]


@router.get('/balance')
async def get_balance(auth: dict = Depends(require_auth)):
    orch = await get_orchestrator()
    return await orch.exchange.get_balance('USDT')


@router.get('/trades')
async def get_trades(limit: int = 100, offset: int = 0):
    rows = execute('SELECT * FROM trades ORDER BY time DESC LIMIT ? OFFSET ?', (limit, offset))
    return rows


@router.get('/stats')
async def get_stats():
    rows = execute('SELECT * FROM daily_stats ORDER BY date DESC LIMIT 30')
    return rows


@router.post('/risk/unlock')
async def unlock_system(req: UnlockRequest, auth: dict = Depends(require_auth)):
    if risk_engine.unlock(req.password):
        return {'status': 'unlocked'}
    raise HTTPException(403, 'Invalid password')


@router.get('/risk/profile')
async def get_risk_profile():
    return risk_engine.config


@router.post('/risk/profile')
async def update_risk_profile(profile: Dict, auth: dict = Depends(require_auth)):
    risk_engine.config.update(profile)
    return {'status': 'updated', 'profile': risk_engine.config}
