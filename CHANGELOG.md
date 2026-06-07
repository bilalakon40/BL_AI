# Changelog / سجل التغييرات

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-06-07

### Added / إضافات
- 🤖 **AI Market Analyzer** - Pluggable multi-backend sentiment analysis
  - Ollama integration (local, free)
  - OpenAI integration (cloud, paid)
  - Rule-based fallback (always works)
- 📊 Batch analysis endpoint (`/api/ai/analyze-batch`)
- 📝 Arabic documentation in `learn/` folder
- 🧪 Test script for AI endpoints

### Changed / تغييرات
- Updated `main.py` to include AI router
- Updated README with AI features

## [1.0.0] - 2026-05-24

### Added / إضافات
- 🚀 Initial release
- 🤖 3 Trading strategies (Grid, Trend, RL)
- 🔌 Multi-exchange support (Bybit, Binance, Paper)
- 🛡️ Risk management engine
- 📱 Telegram bot integration
- 🌐 React + TypeScript dashboard
- 🐳 Docker Compose deployment
- 🔒 JWT auth + AES encryption
- ✅ Test suite (agents, connectors, risk engine)
