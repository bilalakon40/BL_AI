# 🤖 محلل AI للسوق

## ما هذا الموديول؟
ميزة جديدة لمشروع بوت التداول تحلل بيانات السوق وتقدم توصيات (اشترِ / بِعْ / انتظر).

## كيف يعمل؟

```
طلب HTTP → main.py → ai_routes.py → AnalyzerManager
                                              ↓
                              ┌───────────────┼───────────────┐
                              ↓               ↓               ↓
                         Ollama         OpenAI         Rule-based
                        (محلي، مجاني)   (سحابي، مدفوع)   (يعمل دائماً)
```

### 1. `app/ai/analyzer.py` - المنطق الأساسي

يحتوي على:

- **`MarketAnalysis`** - شكل النتيجة (sentiment, action, confidence, reasoning)
- **`BaseAnalyzer`** - قالب مجرد (نفس فكرة `BaseTradingAgent`)
- **`OllamaAnalyzer`** - يستخدم Ollama المحلي (يحتاج Ollama يعمل)
- **`OpenAIAnalyzer`** - يستخدم OpenAI API (يحتاج API Key)
- **`RuleBasedAnalyzer`** - محلل بقواعد بسيطة (يعمل دائماً)
- **`AnalyzerManager`** - يختار أفضل خلفية متاحة تلقائياً

### 2. `app/api/ai_routes.py` - نقاط النهاية (Endpoints)

| المسار | الطريقة | الوظيفة |
|--------|---------|---------|
| `/api/ai/status` | GET | حالة الخلفيات المتاحة |
| `/api/ai/analyze` | POST | تحليل عملة واحدة |
| `/api/ai/analyze-batch` | POST | تحليل عدة عملات |

## كيف تستخدمه؟

### الطريقة 1: من خلال Python
```python
from app.ai.analyzer import AnalyzerManager

manager = AnalyzerManager()
result = manager.analyze('BTCUSDT', {
    'price': 50000,
    'change_24h': 5.2,
    'volume_24h': 1_500_000_000,
})
print(result.action, result.confidence)
print(result.reasoning)  # بالعربية
```

### الطريقة 2: عبر HTTP
```bash
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","market_data":{"price":50000,"change_24h":5.2}}'
```

### الطريقة 3: استخدم سكريبت الاختبار
```bash
# شغّل الخادم في terminal
cd D:\bilal AI\BL_AI\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# في terminal آخر
python D:\bilal AI\BL_AI\learn\07_ai_service\test_ai.py
```

## المفاهيم الجديدة المستخدمة (مهم للفهم)

### 1. Strategy Pattern (نمط الاستراتيجية)
تعدد الخلفيات (Ollama, OpenAI, Rule-based) كلها تتبع نفس الواجهة `BaseAnalyzer`. المدير `AnalyzerManager` يختار الأنسب.

```python
# هذه هي الفكرة
class BaseAnalyzer:        # الواجهة الموحدة
    def analyze(self): pass

class OllamaAnalyzer(BaseAnalyzer):  # استراتيجية 1
    def analyze(self): use_ollama()

class RuleBasedAnalyzer(BaseAnalyzer):  # استراتيجية 2
    def analyze(self): use_rules()
```

### 2. Pluggable Architecture
يمكن إضافة خلفية جديدة (مثل Claude, Gemini) بسهولة:
```python
class ClaudeAnalyzer(BaseAnalyzer):
    def analyze(self):
        # الكود الخاص بـ Claude
        pass

# فقط أضفها للمدير:
manager.analyzers.insert(0, ClaudeAnalyzer())
```

### 3. Fallback Pattern
عند فشل أي خلفية، المدير ينتقل للأخرى تلقائياً. إذا فشلت كلها، يستخدم Rule-based (مضمون العمل).

## القواعد في `RuleBasedAnalyzer`

| الشرط | النتيجة | الثقة |
|------|---------|-------|
| `change_24h > 5%` | BUY + bullish | 70% |
| `change_24h < -5%` | SELL + bearish | 70% |
| `change_24h > 1%` | HOLD + bullish | 55% |
| `change_24h < -1%` | HOLD + bearish | 55% |
| غير ذلك | HOLD + neutral | 50% |

بالإضافة لعوامل ثانوية:
- القرب من أعلى/أدنى 24 ساعة
- حجم التداول

## كيف تضيف Ollama لاحقاً؟

1. تأكد من تشغيل Ollama على `http://localhost:11434`
2. نزل نموذج: `ollama pull llama3.2:1b` (1GB، يعمل على Intel HD)
3. الـ `OllamaAnalyzer` سيكتشفه تلقائياً ويتحول لـ AI حقيقي

## كيف تضيف OpenAI؟

ضع في ملف `.env`:
```
OPENAI_API_KEY=sk-xxxxx
```

ثم:
```python
from app.ai.analyzer import OpenAIAnalyzer
analyzer = OpenAIAnalyzer(model='gpt-4o-mini')
result = analyzer.analyze('BTCUSDT', data)
```

## ملفات المشروع المضافة

```
backend/app/ai/
├── __init__.py         (فارغ - لتعريف المجلد كحزمة Python)
└── analyzer.py         (المنطق الكامل - 360 سطر)

backend/app/api/
└── ai_routes.py        (3 endpoints - 75 سطر)

backend/app/
└── main.py             (مُعدَّل: يضيف ai_router)
```
