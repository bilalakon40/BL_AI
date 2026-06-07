import os
from dotenv import load_dotenv
from typing import Optional


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


class Settings:
    database_path: str = os.getenv('DATABASE_PATH', 'data/trading.db')

    bybit_api_key: Optional[str] = os.getenv('BYBIT_API_KEY')
    bybit_api_secret: Optional[str] = os.getenv('BYBIT_API_SECRET')
    bybit_testnet: bool = os.getenv('BYBIT_TESTNET', 'true').lower() == 'true'

    binance_api_key: Optional[str] = os.getenv('BINANCE_API_KEY')
    binance_api_secret: Optional[str] = os.getenv('BINANCE_API_SECRET')

    telegram_bot_token: Optional[str] = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_admin_chat_id: Optional[str] = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

    admin_password_hash: Optional[str] = os.getenv('ADMIN_PASSWORD_HASH')
    jwt_secret: str = os.getenv('JWT_SECRET', 'change-me-in-production')
    encryption_key: Optional[str] = os.getenv('ENCRYPTION_KEY')

    max_daily_loss_pct: float = float(os.getenv('MAX_DAILY_LOSS_PCT', '0.05'))
    max_position_pct: float = float(os.getenv('MAX_POSITION_PCT', '0.20'))
    kill_switch_loss_pct: float = float(os.getenv('KILL_SWITCH_LOSS_PCT', '0.15'))

    env: str = os.getenv('ENV', 'development')

    ollama_base_url: str = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_model: str = os.getenv('OLLAMA_MODEL', 'llama3')


settings = Settings()
