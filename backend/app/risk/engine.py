import hashlib
from typing import Dict, Tuple
from datetime import datetime


RISK_PROFILE = {
    'max_daily_loss_pct': 0.05,
    'max_position_pct': 0.20,
    'max_open_positions': 3,
    'min_order_size_usdt': 10,
    'max_slippage_pct': 0.005,
    'cooldown_after_loss_minutes': 30,
    'kill_switch_loss_pct': 0.15,
    'allowed_symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT'],
    'allowed_order_types': ['MARKET', 'LIMIT'],
}


class RiskEngine:
    def __init__(self, config: Dict = None):
        self.config = config or RISK_PROFILE
        self.daily_stats = {
            'date': datetime.now().date().isoformat(),
            'starting_balance': 0.0,
            'current_balance': 0.0,
            'trades_count': 0,
            'losses_count': 0,
            'consecutive_losses': 0,
            'total_fees': 0.0,
        }
        self.is_locked = False
        self.lock_reason = None
        self.last_loss_time = None

    def pre_trade_check(self, balance: float, open_positions: int,
                       order_value: float, symbol: str,
                       order_type: str = 'MARKET') -> Tuple[bool, str]:
        if self.is_locked:
            return False, f'SYSTEM LOCKED: {self.lock_reason}'

        if order_value < self.config['min_order_size_usdt']:
            return False, f'Order below minimum: {order_value:.2f} < {self.config["min_order_size_usdt"]}'

        if symbol not in self.config['allowed_symbols']:
            return False, f'Symbol not allowed: {symbol}'

        if order_type not in self.config['allowed_order_types']:
            return False, f'Order type not allowed: {order_type}'

        if open_positions >= self.config['max_open_positions']:
            return False, f'Max positions reached: {open_positions}/{self.config["max_open_positions"]}'

        max_position_value = balance * self.config['max_position_pct']
        if order_value > max_position_value:
            return False, f'Order too large: {order_value:.2f} > {max_position_value:.2f}'

        if self.daily_stats['starting_balance'] > 0:
            daily_pnl = self.daily_stats['current_balance'] - self.daily_stats['starting_balance']
            daily_pnl_pct = daily_pnl / self.daily_stats['starting_balance']
            if daily_pnl_pct <= -self.config['max_daily_loss_pct']:
                self.trigger_lock(f'Daily loss limit reached: {daily_pnl_pct:.2%}')
                return False, self.lock_reason

        if self.daily_stats['consecutive_losses'] >= 3:
            if self.last_loss_time:
                elapsed = (datetime.now() - self.last_loss_time).total_seconds() / 60
                if elapsed < self.config['cooldown_after_loss_minutes']:
                    return False, f'Cooldown active ({elapsed:.0f}/{self.config["cooldown_after_loss_minutes"]} min)'

        return True, 'Risk checks passed'

    def post_trade_update(self, trade_result: Dict):
        self.daily_stats['trades_count'] += 1
        pnl = trade_result.get('pnl', 0)
        balance_after = trade_result.get('balance_after', self.daily_stats['current_balance'])

        self.daily_stats['current_balance'] = balance_after
        self.daily_stats['total_fees'] += trade_result.get('fee', 0)

        if pnl < 0:
            self.daily_stats['losses_count'] += 1
            self.daily_stats['consecutive_losses'] += 1
            self.last_loss_time = datetime.now()
        else:
            self.daily_stats['consecutive_losses'] = 0

        if self.daily_stats['starting_balance'] > 0:
            total_pnl_pct = (balance_after - self.daily_stats['starting_balance']) / self.daily_stats['starting_balance']
            if total_pnl_pct <= -self.config['kill_switch_loss_pct']:
                self.trigger_lock(f'KILL SWITCH: Total loss {total_pnl_pct:.2%}')

    def trigger_lock(self, reason: str):
        self.is_locked = True
        self.lock_reason = reason

    def unlock(self, admin_password: str) -> bool:
        from app.config import settings
        if settings.admin_password_hash:
            stored = settings.admin_password_hash
            candidate = hashlib.sha256(admin_password.encode()).hexdigest()
            if candidate == stored:
                self.is_locked = False
                self.lock_reason = None
                return True
        return False

    def reset_daily(self, new_balance: float):
        self.daily_stats = {
            'date': datetime.now().date().isoformat(),
            'starting_balance': new_balance,
            'current_balance': new_balance,
            'trades_count': 0,
            'losses_count': 0,
            'consecutive_losses': 0,
            'total_fees': 0.0,
        }
        self.is_locked = False
        self.lock_reason = None
        self.last_loss_time = None
