# 🤖 BL_AI - Autonomous AI Trading Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

**منصة تداول عملات رقمية تعمل بالذكاء الاصطناعي على مدار الساعة**
**Autonomous AI-powered cryptocurrency trading platform running 24/7**

[Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [API](#api-documentation) • [Roadmap](#roadmap)

</div>

---

## ⚠️ Disclaimer / تحذير

This software is for **educational purposes only**. Cryptocurrency trading carries significant financial risk. The authors are not responsible for any financial losses incurred from using this software. **Always test on testnet first.**

هذا البرنامج **لأغراض تعليمية فقط**. تداول العملات الرقمية ينطوي على مخاطر مالية كبيرة.

---

## ✨ Features / المميزات

### Core / الأساسي
- 🤖 **4 Trading Strategies** - Grid, Trend Following, Reinforcement Learning, Rule-based
- 🛡️ **Risk Management** - Daily loss limits, position sizing, kill switch
- 📊 **Real-time Dashboard** - React + TypeScript frontend with WebSocket updates
- 📱 **Telegram Bot** - Remote control via /status, /kill, /balance commands
- 🔒 **Security First** - JWT auth, IP whitelisting, AES encryption for API keys

### AI & Analytics / الذكاء الاصطناعي
- 🧠 **AI Market Analyzer** - Pluggable multi-backend sentiment analysis
  - **Ollama** (local, free, private)
  - **OpenAI** (cloud, powerful)
  - **Rule-based** (always works, no dependencies)
- 🔌 **Pluggable Architecture** - Add new AI providers in minutes
- 📈 **Batch Analysis** - Analyze multiple symbols in one request

### Infrastructure / البنية التحتية
- 🐳 **Docker** - One-command deployment
- 💾 **SQLite** - Zero-config database (PostgreSQL-ready)
- 🔌 **Multi-Exchange** - Bybit, Binance, Paper Trading (CCXT)
- 🌐 **WebSocket** - Real-time price feeds and order updates

---

## 🏗️ Architecture / البنية

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Dashboard (React)                │
│                       :3000 - WebSocket                      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Python) :8000                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │ AI Engine  │  │ Risk Engine│  │ Orchestrtr │             │
│  │ (Ollama,   │  │ (Limits,   │  │ (Agent     │             │
│  │  OpenAI,   │  │  Kill      │  │  Manager)  │             │
│  │  Rules)    │  │  Switch)   │  │            │             │
│  └────────────┘  └────────────┘  └────────────┘             │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐    ┌──────────┐    ┌──────────┐
   │ Bybit   │    │ Binance  │    │  Paper   │
   │ API     │    │  API     │    │ Trading  │
   └─────────┘    └──────────┘    └──────────┘
```

### Project Structure / هيكل المشروع

```
BL_AI/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── ai/              # 🆕 AI Market Analyzer
│   │   │   └── analyzer.py  # Multi-backend AI system
│   │   ├── agents/          # Trading strategies
│   │   │   ├── base_agent.py
│   │   │   ├── grid_agent.py
│   │   │   ├── trend_agent.py
│   │   │   └── rl_agent.py
│   │   ├── api/             # API routes
│   │   │   ├── routes.py
│   │   │   ├── ai_routes.py # 🆕 AI endpoints
│   │   │   └── websocket.py
│   │   ├── connectors/      # Exchange integrations
│   │   ├── core/            # Orchestrator + order manager
│   │   ├── db/              # Database models
│   │   ├── risk/            # Risk engine
│   │   ├── security/        # Auth + encryption
│   │   ├── utils/           # Logger + helpers
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                # React + TypeScript dashboard
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── telegram-bot/            # Telegram control bot
│   ├── bot.py
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🚀 Quick Start / البدء السريع

### Prerequisites / المتطلبات
- Python 3.12+
- Node.js 18+ (for frontend)
- Docker (optional, for containerized deployment)
- Git

### Installation / التثبيت

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/BL_AI.git
cd BL_AI

# 2. Setup environment
cp .env.example .env
# Edit .env with your API keys (or use testnet defaults)

# 3. Backend
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. Frontend (new terminal)
cd frontend
npm install
npm run dev

# 5. Telegram bot (new terminal, optional)
cd telegram-bot
pip install -r requirements.txt
python bot.py
```

### Docker (One-Command) / Docker

```bash
docker-compose up -d
```

---

## 📚 API Documentation / توثيق الـ API

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### AI Endpoints / نقاط نهاية AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ai/status` | Check available AI backends |
| POST | `/api/ai/analyze` | Analyze single symbol |
| POST | `/api/ai/analyze-batch` | Analyze multiple symbols |

#### Example: Analyze BTC
```bash
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "market_data": {
      "price": 50000,
      "change_24h": 5.2,
      "volume_24h": 2000000000,
      "high_24h": 51000,
      "low_24h": 49000
    }
  }'
```

Response:
```json
{
  "symbol": "BTCUSDT",
  "sentiment": "bullish",
  "confidence": 0.7,
  "action": "BUY",
  "reasoning": "بناءً على تغير +5.20% في 24 ساعة، السوق في اتجاه صاعد.",
  "key_factors": ["صعود قوي: +5.2% في 24 ساعة", "حجم تداول مرتفع يدعم الحركة"],
  "risks": [],
  "backend": "rule_based"
}
```

### Trading Endpoints / نقاط نهاية التداول

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/balance` | Account balance |
| GET | `/api/trades` | Trade history |
| GET | `/api/stats` | Performance statistics |
| POST | `/api/orchestrator/start` | Start trading bot |
| POST | `/api/orchestrator/stop` | Emergency stop |
| GET | `/api/orchestrator/state` | Get current state |
| POST | `/api/agents/create` | Create new trading agent |

### Telegram Commands / أوامر تيلغرام

| Command | Description |
|---------|-------------|
| `/start` | Show available commands |
| `/status` | System status (running, locked, agents) |
| `/kill` | Emergency stop all trading |
| `/balance` | Account balance |
| `/agents` | List active agents with performance |
| `/unlock <password>` | Unlock system after kill switch |

---

## 🔧 Configuration / الإعدادات

Edit `.env` file:

```bash
# Database
DATABASE_PATH=data/trading.db

# Exchange APIs (use TESTNET first!)
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret
BYBIT_TESTNET=true

BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ADMIN_CHAT_ID=your_chat_id

# Security
ADMIN_PASSWORD_HASH=sha256_of_your_password
JWT_SECRET=random_64_char_string
ENCRYPTION_KEY=your_encryption_key

# Risk Management
MAX_DAILY_LOSS_PCT=0.05       # 5% max daily loss
MAX_POSITION_PCT=0.20          # 20% max position size
KILL_SWITCH_LOSS_PCT=0.15     # Stop at 15% loss

# AI (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

## 🧪 Testing / الاختبار

```bash
cd backend
pytest tests/ -v
```

Current test coverage:
- `test_agents.py` - Trading agent logic
- `test_connectors.py` - Exchange connectors
- `test_risk_engine.py` - Risk management rules

---

## 🛣️ Roadmap / خارطة الطريق

### ✅ Completed / مكتمل
- [x] Multi-exchange support (Bybit, Binance, Paper)
- [x] 3 trading strategies (Grid, Trend, RL)
- [x] Risk management engine
- [x] Telegram bot integration
- [x] Web dashboard (React)
- [x] Docker deployment
- [x] **AI Market Analyzer** (Ollama + OpenAI + Rule-based)
- [x] Pluggable AI architecture

### 🚧 In Progress / قيد التطوير
- [ ] Real-time price feed integration
- [ ] Backtesting engine
- [ ] Advanced RL agent with PyTorch
- [ ] Mobile app (React Native)

### 📋 Planned / مخطط
- [ ] Multi-language support (AR, EN, FR)
- [ ] User authentication system
- [ ] Subscription billing (Stripe)
- [ ] Cloud deployment templates (AWS, GCP, Azure)
- [ ] Strategy marketplace

---

## 🤝 Contributing / المساهمة

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License / الترخيص

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact / التواصل

- **GitHub**: [@yourusername](https://github.com/yourusername)
- **Email**: your.email@example.com
- **Telegram**: @yourusername

---

## 🙏 Acknowledgments / شكر

- [CCXT](https://github.com/ccxt/ccxt) - Unified exchange API
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Ollama](https://ollama.com/) - Local LLM runner
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram bot library

---

<div align="center">

**Built with ❤️ for the open-source trading community**
**صُنع بـ ❤️ لمجتمع التداول مفتوح المصدر**

⭐ Star this repo if you find it useful!

</div>
