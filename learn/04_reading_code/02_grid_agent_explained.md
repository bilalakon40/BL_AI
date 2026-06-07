# شرح ملف `grid_agent.py` - استراتيجية الشبكة

## ما هي استراتيجية الشبكة (Grid Trading)؟

تخيل سُلَّم بين سعر منخفض وسعر مرتفع. كل درجة من السلم = "مستوى شبكة".

**الفكرة:**
- السعر يرتفع وينزل داخل نطاق معين
- اشترِ عند درجة منخفضة، بِعْ عند درجة عالية
- كل مرة يقطع فيها السعر درجة = ربح صغير

**مثال عملي:**
- حدد النطاق: بين 45,000$ و 55,000$
- قسّمه إلى 10 درجات (شبكة)
- كل درجة = 1,000$
- إذا وصل السعر لـ 46,000$ → اشترِ
- إذا وصل لـ 55,000$ → بِعْ

## السطر بسطر:

```python
# سطر 1-2: الاستيرادات
from typing import Dict, List
from .base_agent import BaseTradingAgent, AgentDecision
# النقطة (.) قبل base_agent تعني: من نفس المجلد


# سطر 5-14: المُنشئ (Constructor)
class GridTradingAgent(BaseTradingAgent):
    """
    يرث من BaseTradingAgent
    يعني: يأخذ كل خصائصه (agent_id, performance) ويُضيف عليها
    """
    def __init__(self, agent_id: str, symbol: str, config: Dict):
        # super() = استدعاء دالة الأب
        # نُمرر agent_id و strategy='grid'
        super().__init__(agent_id, 'grid')

        # معلومات خاصة بالشبكة:
        self.symbol = symbol                          # مثلاً "BTCUSDT"
        self.upper_price = config['upper_price']      # الحد الأعلى
        self.lower_price = config['lower_price']      # الحد الأدنى
        self.grid_count = config.get('grid_count', 10) # عدد الدرجات (افتراضي 10)
        self.grids = self._calculate_grids()          # حساب الدرجات
        self.active_orders: Dict[float, str] = {}     # الأوامر النشطة
        self.holdings = 0.0                           # الكمية المملوكة


    # سطر 16-18: حساب الدرجات
    def _calculate_grids(self) -> List[float]:
        """
        الدوال التي تبدأ بـ _ (underscore) في Python = "خاصة" (private)
        يعني: لا تستدعيها من خارج الكلاس (اتفاق برمجي)
        """
        step = (self.upper_price - self.lower_price) / self.grid_count
        # مثال: (55000 - 45000) / 10 = 1000

        return [self.lower_price + (step * i) for i in range(self.grid_count + 1)]
        # List Comprehension (مهم جداً في Python!):
        #   [صيغة for عنصر in تسلسل]
        # النتيجة: [45000, 46000, 47000, ..., 55000]


    # سطر 20-57: الدالة الأهم - التحليل واتخاذ القرار
    async def analyze(self, market_data: Dict, portfolio_state: Dict) -> AgentDecision:
        """
        تُستدعى كل ثانية (أو كل دقيقة، حسب الإعداد) لتحليل السوق
        """
        current_price = market_data.get('price', 0)        # السعر الحالي
        balance = portfolio_state.get('balance', 0)        # رصيدك

        # 1) البحث عن فرص الشراء
        # شرط: الدرجة أقل من السعر الحالي + لم نُنفذ أمر عليها
        buy_candidates = [
            g for g in self.grids
            if g < current_price and g not in self.active_orders
        ]

        # 2) البحث عن فرص البيع
        # شرط: الدرجة أعلى من السعر + عندنا أمر نشط عليها
        sell_candidates = [
            g for g in self.grids
            if g > current_price and g in self.active_orders
        ]

        # 3) قرار الشراء
        if buy_candidates and balance > 10:    # عندنا على الأقل 10$ رصيد
            target = max(buy_candidates)        # أعلى درجة (أقرب للسعر)
            qty = (balance * 0.1) / target     # 10% من الرصيد / السعر
            self.active_orders[target] = 'pending'

            return AgentDecision(
                action='BUY',                  # قرار: اشترِ
                confidence=0.8,                # ثقة 80%
                symbol=self.symbol,
                qty=qty,
                order_type='LIMIT',            # أمر محدد السعر
                price=target,                  # السعر المستهدف
                reasoning=f'Grid buy at level {target:.2f}',
                strategy='grid',
            )

        # 4) قرار البيع
        if sell_candidates and self.holdings > 0:
            target = min(sell_candidates)
            qty = self.holdings / max(len(sell_candidates), 1)
            self.active_orders[target] = 'pending'

            return AgentDecision(
                action='SELL',
                confidence=0.8,
                symbol=self.symbol,
                qty=qty,
                order_type='LIMIT',
                price=target,
                reasoning=f'Grid sell at level {target:.2f}',
                strategy='grid',
            )

        # 5) لا فرصة → انتظر
        return AgentDecision(
            action='HOLD',                      # لا تفعل شيئاً
            confidence=0.5,
            symbol=self.symbol,
            qty=0,
            order_type='MARKET',
            price=None,
            reasoning='No grid level triggered',
            strategy='grid',
        )


    # سطر 59-67: تُستدعى بعد تنفيذ الأمر
    def on_order_executed(self, decision: 'AgentDecision', result: dict):
        """
        المنصة تستدعي هذه الدالة بعد تنفيذ الأمر
        لنُحدّث حالتنا
        """
        price = decision.price or result.get('price', 0)
        qty = result.get('qty', decision.qty)

        if decision.action == 'BUY' and price in self.active_orders:
            del self.active_orders[price]   # احذف الأمر النشط
            self.holdings += qty            # زد الكمية المملوكة

        elif decision.action == 'SELL' and price in self.active_orders:
            del self.active_orders[price]
            self.holdings = max(0, self.holdings - qty)  # قلل الكمية


    # سطر 69-70: تدريب (لا شيء - Grid لا يتعلم)
    async def train(self, historical_data: List[Dict]):
        pass    # Grid استراتيجية ثابتة، لا تحتاج تعلّم
```

## المفاهيم المهمة الجديدة:

### 1. `super().__init__(...)` (سطر 8)
```python
class GridTradingAgent(BaseTradingAgent):
    def __init__(self, ...):
        super().__init__(agent_id, 'grid')  # ← هذا السطر
        # يستدعي __init__ الخاص بالأب
        # لتهيئة الخصائص الموروثة (agent_id, performance, is_active)
```

### 2. `config.get('grid_count', 10)` (سطر 11)
```python
# الفرق المهم:
config['grid_count']        # ❌ يرمي خطأ إذا المفتاح غير موجود
config.get('grid_count', 10) # ✓ يرجع 10 إذا المفتاح غير موجود
```

### 3. List Comprehension (سطر 18)
```python
# الطريقة العادية:
result = []
for i in range(11):
    result.append(45000 + (1000 * i))

# بطريقة Python (أسرع وأجمل):
result = [45000 + (1000 * i) for i in range(11)]
```

### 4. `max(self.holdings - qty, 0)` (سطر 67)
لا نريد holdings تكون سالبة. `max(x, 0)` تعني: "خذ الأكبر بين x و 0".

### 5. `or` (سطر 60)
```python
price = decision.price or result.get('price', 0)
# معناه: إذا decision.price فارغ (None أو 0)، استخدم القيمة الثانية
```

## ملخص استراتيجيات الوكلاء:

| الاستراتيجية | المبدأ | متى تنجح؟ |
|--------------|--------|-----------|
| Grid | شراء/بيع على مستويات ثابتة | السوق يتذبذب في نطاق |
| Trend | تتبع الاتجاه (صاعد أو هابط) | السوق في ترند واضح |
| RL | يتعلم من البيانات (Reinforcement Learning) | مع بيانات تاريخية كافية |

## أين تذهب البيانات؟
1. الوكيل يُرجع `AgentDecision`
2. `OrderManager` يستقبله ويتحقق من `RiskEngine`
3. إذا موافق → يُرسل الأمر لـ `Connector` (Binance/Bybit)
4. `Connector` ينفذ الأمر ويرجع النتيجة
5. `on_order_executed` تُستدعى لتحديث الحالة
