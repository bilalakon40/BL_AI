from app.risk.engine import RiskEngine, RISK_PROFILE


def test_daily_loss_limit():
    risk = RiskEngine(RISK_PROFILE)
    risk.daily_stats['starting_balance'] = 1000
    risk.daily_stats['current_balance'] = 949
    allowed, reason = risk.pre_trade_check(949, 0, 100, 'BTCUSDT')
    assert allowed == False
    assert 'Daily loss limit' in reason


def test_kill_switch():
    risk = RiskEngine(RISK_PROFILE)
    risk.daily_stats['starting_balance'] = 1000
    risk.post_trade_update({'pnl': -160, 'balance_after': 840})
    assert risk.is_locked == True
    assert 'KILL SWITCH' in risk.lock_reason


def test_max_positions():
    risk = RiskEngine(RISK_PROFILE)
    risk.daily_stats['starting_balance'] = 1000
    risk.daily_stats['current_balance'] = 1000
    allowed, reason = risk.pre_trade_check(1000, 3, 100, 'BTCUSDT')
    assert allowed == False
    assert 'Max positions' in reason


def test_max_position_size():
    risk = RiskEngine(RISK_PROFILE)
    risk.daily_stats['starting_balance'] = 1000
    risk.daily_stats['current_balance'] = 1000
    allowed, reason = risk.pre_trade_check(1000, 0, 500, 'BTCUSDT')
    assert allowed == False
    assert 'Order too large' in reason


def test_allowed_symbols():
    risk = RiskEngine(RISK_PROFILE)
    risk.daily_stats['starting_balance'] = 1000
    risk.daily_stats['current_balance'] = 1000
    allowed, reason = risk.pre_trade_check(1000, 0, 100, 'DOGEUSDT')
    assert allowed == False
    assert 'Symbol not allowed' in reason


def test_min_order_size():
    risk = RiskEngine(RISK_PROFILE)
    risk.daily_stats['starting_balance'] = 1000
    risk.daily_stats['current_balance'] = 1000
    allowed, reason = risk.pre_trade_check(1000, 0, 5, 'BTCUSDT')
    assert allowed == False
    assert 'Order below minimum' in reason


def test_consecutive_losses_cooldown():
    risk = RiskEngine(RISK_PROFILE)
    risk.daily_stats['starting_balance'] = 1000
    risk.daily_stats['current_balance'] = 990
    risk.daily_stats['consecutive_losses'] = 3
    risk.last_loss_time = __import__('datetime').datetime.now()
    allowed, reason = risk.pre_trade_check(990, 0, 100, 'BTCUSDT')
    assert allowed == False
    assert 'Cooldown' in reason


def test_system_locked():
    risk = RiskEngine(RISK_PROFILE)
    risk.is_locked = True
    risk.lock_reason = 'Manual lock'
    allowed, reason = risk.pre_trade_check(1000, 0, 100, 'BTCUSDT')
    assert allowed == False
    assert 'SYSTEM LOCKED' in reason


def test_order_type_not_allowed():
    risk = RiskEngine(RISK_PROFILE)
    risk.daily_stats['starting_balance'] = 1000
    risk.daily_stats['current_balance'] = 1000
    allowed, reason = risk.pre_trade_check(1000, 0, 100, 'BTCUSDT', 'STOP')
    assert allowed == False
    assert 'Order type not allowed' in reason


def test_post_trade_win():
    risk = RiskEngine(RISK_PROFILE)
    risk.daily_stats['starting_balance'] = 1000
    risk.daily_stats['current_balance'] = 1000
    risk.post_trade_update({'pnl': 50, 'balance_after': 1050, 'fee': 1})
    assert risk.daily_stats['trades_count'] == 1
    assert risk.daily_stats['consecutive_losses'] == 0


def test_post_trade_loss():
    risk = RiskEngine(RISK_PROFILE)
    risk.daily_stats['starting_balance'] = 1000
    risk.daily_stats['current_balance'] = 1000
    risk.post_trade_update({'pnl': -30, 'balance_after': 970, 'fee': 1})
    assert risk.daily_stats['consecutive_losses'] == 1


def test_reset_daily():
    risk = RiskEngine(RISK_PROFILE)
    risk.is_locked = True
    risk.reset_daily(5000)
    assert risk.is_locked == False
    assert risk.daily_stats['starting_balance'] == 5000
    assert risk.daily_stats['consecutive_losses'] == 0


def test_risk_profile_defaults():
    risk = RiskEngine()
    assert risk.config['max_daily_loss_pct'] == 0.05
    assert risk.config['max_open_positions'] == 3
    assert 'BTCUSDT' in risk.config['allowed_symbols']
