# خريطة المشروع - بوت التداول الذكي

## ما هذا المشروع؟
منصة تداول عملات رقمية تعمل تلقائياً بالذكاء الاصطناعي. مثل "موظف" يفتح ويغلق صفقات 24/7.

## كيف تتدفق البيانات؟

```
المتداول (أنت)
     ↓ (أوامر)
Telegram Bot ──────→ Backend (FastAPI) ──────→ Database
     ↓                    ↓                       ↑
Dashboard (React) ──→ Risk Engine               Orders
     ↓                    ↓                      
   Ollama (AI) ──────→ Trading Agents ──────→ Exchanges
                       (Grid, Trend, RL)        (Bybit, Binance)
```

## شرح كل مجلد (Folder)

### 📁 `backend/app/` - العقل المدبر
كل المنطق البرمجي موجود هنا:

- **`config.py`** - يقرأ الإعدادات من ملف `.env` (مفاتيح API، إعدادات المخاطر)
- **`main.py`** - نقطة البداية، يَشغّل الخادم (server)
- **`agents/`** - استراتيجيات التداول (3 أنواع):
  - `base_agent.py` - القالب الأساسي للوكلاء
  - `grid_agent.py` - استراتيجية الشبكة (شراء/بيع على مستويات محددة)
  - `trend_agent.py` - استراتيجية تتبع الترند
  - `rl_agent.py` - وكيل تعلّم معزز (Reinforcement Learning)
- **`connectors/`** - الاتصال بمنصات التداول:
  - `base_exchange.py` - قالب أساسي
  - `binance_connector.py` - منصة Binance
  - `bybit_connector.py` - منصة Bybit
  - `paper_trading.py` - تداول وهمي (للتجربة بدون مخاطرة)
- **`core/`** - المنسق الرئيسي:
  - `orchestrator.py` - يدير تشغيل/إيقاف الوكلاء
  - `order_manager.py` - يدير الأوامر (شراء/بيع)
- **`db/`** - قاعدة البيانات:
  - `database.py` - الاتصال بـ SQLite
  - `models.py` - شكل الجداول (أوامر، صفقات، سجلات)
- **`risk/`** - الأمان:
  - `engine.py` - يطبق قواعد الأمان (حد خسارة، kill switch)
- **`security/`** - الأمان السيبراني:
  - `auth.py` - المصادقة (من يستطيع الدخول)
  - `encryption.py` - تشفير المفاتيح
- **`api/`** - الواجهات البرمجية:
  - `routes.py` - المسارات (URLs) - أوامر GET/POST
  - `websocket.py` - اتصال مباشر (لوحة التحكم)
- **`utils/`** - أدوات مساعدة:
  - `logger.py` - تسجيل الأحداث (ماذا حدث ومتى)

### 📁 `frontend/` - لوحة التحكم (UI)
- مبني بـ React + TypeScript + Tailwind
- تعرض البيانات بشكل مرئي (رسوم بيانية، حالة الحساب)

### 📁 `telegram-bot/` - التحكم عن بعد
- `bot.py` - بوت تلغرام يعطيك أوامر مثل `/status` و `/kill`

### 📁 `models/` - نماذج AI محلية
- مكان لتخزين نماذج Ollama

### 📁 `secrets/` - الأسرار
- مفاتيح مشفرة (لا تشاركها أبداً!)

## المكدس التقني (Tech Stack)

| المكوّن | التقنية | الاستخدام |
|---------|---------|-----------|
| Backend | FastAPI | خادم API سريع وحديث |
| Database | SQLite | تخزين بيانات خفيف |
| AI | Ollama (محلي) | نماذج LLM محلية |
| Exchange | CCXT | مكتبة موحدة للمنصات |
| Bot | python-telegram-bot | واجهة تلغرام |
| Frontend | React + Vite | واجهة حديثة وسريعة |
| Container | Docker | تشغيل في بيئات معزولة |
| Tests | pytest | اختبارات تلقائية |
