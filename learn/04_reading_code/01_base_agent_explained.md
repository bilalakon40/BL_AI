# شرح ملف `base_agent.py` - القالب الأساسي للوكلاء

## ما هذا الملف؟
هذا هو **القالب (Template)** الذي يبني عليه جميع وكلاء التداول الثلاثة (Grid, Trend, RL).

## السطر بسطر (بالعربية):

```python
# سطر 1-3: استيراد أدوات جاهزة
from abc import ABC, abstractmethod       # ABC = Abstract Base Class (لإنشاء قالب)
from typing import Dict, List, Optional   # أنواع البيانات (قاموس، قائمة، اختياري)
from dataclasses import dataclass, field  # dataclass = طريقة سهلة لإنشاء كلاسات


# سطر 6-16: شكل "القرار" الذي يتخذه الوكيل
@dataclass
class AgentDecision:
    """
    عندما يفكر الوكيل ويقرر، يُرجع "قرار" يحتوي:
    - action: ماذا يفعل؟ (buy, sell, hold)
    - confidence: كم واثق من قراره؟ (0.0 إلى 1.0)
    - symbol: أي عملة؟ (مثل BTCUSDT)
    - qty: كم يشتري/يبيع؟
    - order_type: نوع الأمر (market = فوري، limit = بسعر محدد)
    - price: السعر المحدد (للأوامر المحددة)
    - reasoning: لماذا اتخذ هذا القرار؟ (مهم جداً!)
    - strategy: أي استراتيجية؟
    - metadata: معلومات إضافية
    """
    action: str
    confidence: float
    symbol: str
    qty: float
    order_type: str
    price: Optional[float] = None
    reasoning: str = ''
    strategy: str = ''
    metadata: Dict = field(default_factory=dict)


# سطر 19-46: القالب الأساسي لجميع الوكلاء
class BaseTradingAgent(ABC):
    """
    ABC = Abstract Base Class
    يعني: لا يمكنك إنشاء "وكيل أساسي" مباشرة
    يجب أن ترث (inherit) منه وتُعرّف (implement) الدوال المجردة
    """

    def __init__(self, agent_id: str, strategy: str):
        # كل وكيل له:
        # - agent_id: اسم فريد (مثل "trend_btc_01")
        # - strategy: نوع الاستراتيجية ("grid", "trend", "rl")
        # - is_active: هل يعمل الآن؟
        # - performance: أداؤه (عدد الصفقات، الأرباح، نسبة النجاح)
        self.agent_id = agent_id
        self.strategy = strategy
        self.is_active = False
        self.performance = {
            'trades': 0,         # عدد الصفقات
            'wins': 0,           # عدد الصفقات الرابحة
            'total_pnl': 0.0,    # إجمالي الربح/الخسارة
            'win_rate': 0.0,     # نسبة النجاح
        }

    @abstractmethod
    async def analyze(self, market_data: Dict, portfolio_state: Dict) -> AgentDecision:
        # الدالة المجردة: كل وكيل يجب أن يطبقها
        # تُستدعى لتحليل السوق واتخاذ قرار
        pass

    @abstractmethod
    async def train(self, historical_data: List[Dict]):
        # الدالة المجردة: لتدريب النموذج (للـ RL agent مثلاً)
        pass

    def on_order_executed(self, decision: 'AgentDecision', result: dict):
        # تُستدعى بعد تنفيذ الأمر
        # الوكيل يتعلم من النتيجة
        pass

    def update_performance(self, pnl: float):
        # تحديث الإحصائيات بعد كل صفقة
        # pnl = Profit and Loss (ربح أو خسارة)
        self.performance['trades'] += 1
        self.performance['total_pnl'] += pnl
        if pnl > 0:    # إذا كان ربحاً
            self.performance['wins'] += 1
        # حساب نسبة النجاح بدقة
        self.performance['win_rate'] = (
            self.performance['wins'] / self.performance['trades']
            if self.performance['trades'] > 0 else 0.0
        )
```

## المفاهيم الجديدة هنا (مهمة جداً):

### 1. `@dataclass` (سطر 6)
بدل ما تكتب `__init__` و `__repr__` يدوياً، Python يفعلها لك:

```python
@dataclass
class AgentDecision:
    action: str
    confidence: float

# بدلاً من:
class AgentDecision:
    def __init__(self, action, confidence):
        self.action = action
        self.confidence = confidence
```

### 2. `@abstractmethod` (سطر 28)
دالة **بدون كود** - كل وكيل يجب أن يكتبها بطريقته. مثل "عقد" يقول: "كل وكيل يجب أن يطبق `analyze()`".

### 3. `Optional[float] = None` (سطر 13)
معناها: السعر **اختياري**، يمكن أن يكون `None` (فارغ) إذا كان `order_type="market"`.

### 4. `field(default_factory=dict)` (سطر 16)
لاحظ الفرق:
- `metadata: Dict = {}`  ❌ خطأ شائع (متغير مشترك بين الكائنات!)
- `metadata: Dict = field(default_factory=dict)`  ✓ صحيح (قاموس جديد لكل كائن)

## أين يُستخدم هذا الملف؟
- في `grid_agent.py` (استراتيجية الشبكة)
- في `trend_agent.py` (استراتيجية الترند)
- في `rl_agent.py` (التعلم المعزز)

## تمرين: افتح الملفات الثلاثة الأخرى
- `grid_agent.py` (2884 bytes)
- `trend_agent.py` (4787 bytes)
- `rl_agent.py` (4142 bytes)

كلها ترث من `BaseTradingAgent` وتطبق `analyze()` بطريقتها.
