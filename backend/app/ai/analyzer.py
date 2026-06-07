"""
محلل السوق بالذكاء الاصطناعي
============================

يدعم ثلاث خلفيات (backends):
1. Ollama محلي (مجاني، خاص)
2. OpenAI API (مدفوع، قوي)
3. محلل بسيط مدمج (يعمل دائماً)

المفاهيم المستخدمة:
- Abstract Base Class (نفس base_agent)
- Strategy Pattern (تبديل الخلفيات بسهولة)
- Dataclass (لنتائج التحليل)
- Error Handling (التعامل مع الأخطاء)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import json
import os
import re


@dataclass
class MarketAnalysis:
    """
    نتيجة تحليل السوق
    ==================

    المشاعر (Sentiment): هل السوق صاعد أم هابط؟
    - bullish: صاعد (اشترِ)
    - bearish: هابط (بِعْ)
    - neutral: محايد (انتظر)
    """
    symbol: str
    sentiment: str         # bullish / bearish / neutral
    confidence: float      # 0.0 إلى 1.0
    action: str            # BUY / SELL / HOLD
    reasoning: str         # السبب بالعربية أو الإنجليزية
    key_factors: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    backend: str = 'unknown'
    raw_response: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# القالب الأساسي (Abstract Base Class)
# ============================================================================

class BaseAnalyzer(ABC):
    """القالب الذي ترث منه جميع الخلفيات"""

    def __init__(self, name: str):
        self.name = name
        self.is_available = False

    @abstractmethod
    def is_ready(self) -> bool:
        """هل هذه الخلفية جاهزة للاستخدام؟"""
        pass

    @abstractmethod
    def analyze(self, symbol: str, market_data: Dict, context: Optional[Dict] = None) -> MarketAnalysis:
        """حلل السوق وأرجع نتيجة"""
        pass

    def _build_prompt(self, symbol: str, market_data: Dict, context: Optional[Dict] = None) -> str:
        """
        بناء البرومبت (Prompt) للنموذج
        ==============================
        البرومبت = التعليمات التي نرسلها للنموذج
        """
        price = market_data.get('price', 0)
        change_24h = market_data.get('change_24h', 0)
        volume_24h = market_data.get('volume_24h', 0)
        high_24h = market_data.get('high_24h', price)
        low_24h = market_data.get('low_24h', price)

        prompt = f"""حلل بيانات السوق التالية لـ {symbol}:

السعر الحالي: ${price:,.2f}
التغير 24 ساعة: {change_24h:+.2f}%
أعلى سعر 24 ساعة: ${high_24h:,.2f}
أدنى سعر 24 ساعة: ${low_24h:,.2f}
حجم التداول 24 ساعة: ${volume_24h:,.0f}
"""
        if context and context.get('news'):
            prompt += f"\nأخبار حديثة:\n{context['news']}\n"

        prompt += """
أرجع JSON فقط بهذا الشكل:
{
    "sentiment": "bullish أو bearish أو neutral",
    "confidence": رقم من 0.0 إلى 1.0,
    "action": "BUY أو SELL أو HOLD",
    "reasoning": "سبب القرار بالعربية",
    "key_factors": ["عامل 1", "عامل 2", "عامل 3"],
    "risks": ["خطر 1", "خطر 2"]
}
"""
        return prompt

    def _parse_json_response(self, response: str) -> Dict:
        """استخرج JSON من رد النموذج (قد يحوي نص إضافي)"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(f"لم يتم العثور على JSON في الرد: {response[:200]}")


# ============================================================================
# الخلفية 1: Ollama (محلية، مجانية)
# ============================================================================

class OllamaAnalyzer(BaseAnalyzer):
    """
    يستخدم Ollama المحلي لتحليل السوق
    Ollama = تطبيق لتشغيل نماذج LLM محلياً
    """

    def __init__(self, base_url: str = None, model: str = 'llama3'):
        super().__init__('ollama')
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3')

    def is_ready(self) -> bool:
        """تحقق هل Ollama يعمل ويستجيب"""
        try:
            import httpx
            resp = httpx.get(f'{self.base_url}/api/tags', timeout=3)
            self.is_available = resp.status_code == 200
            return self.is_available
        except Exception:
            self.is_available = False
            return False

    def analyze(self, symbol: str, market_data: Dict, context: Optional[Dict] = None) -> MarketAnalysis:
        import httpx

        prompt = self._build_prompt(symbol, market_data, context)

        try:
            resp = httpx.post(
                f'{self.base_url}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'format': 'json',
                },
                timeout=60,
            )
            resp.raise_for_status()
            response_text = resp.json().get('response', '')
            data = self._parse_json_response(response_text)

            return MarketAnalysis(
                symbol=symbol,
                sentiment=data.get('sentiment', 'neutral'),
                confidence=float(data.get('confidence', 0.5)),
                action=data.get('action', 'HOLD'),
                reasoning=data.get('reasoning', ''),
                key_factors=data.get('key_factors', []),
                risks=data.get('risks', []),
                backend='ollama',
                raw_response=response_text,
            )
        except Exception as e:
            raise RuntimeError(f"Ollama analysis failed: {e}")


# ============================================================================
# الخلفية 2: OpenAI (سحابية، مدفوعة)
# ============================================================================

class OpenAIAnalyzer(BaseAnalyzer):
    """
    يستخدم OpenAI API (GPT-4, GPT-4o-mini, etc)
    يحتاج API Key في متغير OPENAI_API_KEY
    """

    def __init__(self, api_key: str = None, model: str = 'gpt-4o-mini'):
        super().__init__('openai')
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model

    def is_ready(self) -> bool:
        if not self.api_key:
            self.is_available = False
            return False
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            self._client = client
            self.is_available = True
            return True
        except Exception:
            self.is_available = False
            return False

    def analyze(self, symbol: str, market_data: Dict, context: Optional[Dict] = None) -> MarketAnalysis:
        from openai import OpenAI

        client = self._client if hasattr(self, '_client') else OpenAI(api_key=self.api_key)
        prompt = self._build_prompt(symbol, market_data, context)

        try:
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': 'أنت محلل أسواق مالية محترف. أرجع JSON فقط.'},
                    {'role': 'user', 'content': prompt},
                ],
                response_format={'type': 'json_object'},
                timeout=60,
            )
            response_text = resp.choices[0].message.content
            data = self._parse_json_response(response_text)

            return MarketAnalysis(
                symbol=symbol,
                sentiment=data.get('sentiment', 'neutral'),
                confidence=float(data.get('confidence', 0.5)),
                action=data.get('action', 'HOLD'),
                reasoning=data.get('reasoning', ''),
                key_factors=data.get('key_factors', []),
                risks=data.get('risks', []),
                backend='openai',
                raw_response=response_text,
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI analysis failed: {e}")


# ============================================================================
# الخلفية 3: محلل بسيط (يعمل دائماً)
# ============================================================================

class RuleBasedAnalyzer(BaseAnalyzer):
    """
    محلل قائم على القواعد - يعمل بدون AI
    ======================================

    يحلل البيانات بقواعد بسيطة:
    - تغير السعر > 5% = إشارة قوية
    - حجم التداول مرتفع = تأكيد
    - القرب من أعلى/أدنى 24 ساعة = مؤشر

    مفيد كـ:
    - Fallback عندما لا تتوفر خلفيات أخرى
    - أداة تعليمية لفهم منطق التداول
    """

    def __init__(self):
        super().__init__('rule_based')

    def is_ready(self) -> bool:
        self.is_available = True
        return True

    def analyze(self, symbol: str, market_data: Dict, context: Optional[Dict] = None) -> MarketAnalysis:
        price = market_data.get('price', 0)
        change_24h = market_data.get('change_24h', 0)
        volume_24h = market_data.get('volume_24h', 0)
        high_24h = market_data.get('high_24h', price)
        low_24h = market_data.get('low_24h', price)

        # القواعد
        key_factors = []
        risks = []

        # قاعدة 1: التغير السعري
        if change_24h > 5:
            sentiment = 'bullish'
            action = 'BUY'
            confidence = 0.7
            key_factors.append(f'صعود قوي: +{change_24h:.1f}% في 24 ساعة')
        elif change_24h < -5:
            sentiment = 'bearish'
            action = 'SELL'
            confidence = 0.7
            key_factors.append(f'هبوط قوي: {change_24h:.1f}% في 24 ساعة')
        elif change_24h > 1:
            sentiment = 'bullish'
            action = 'HOLD'
            confidence = 0.55
            key_factors.append(f'صعود طفيف: +{change_24h:.1f}%')
        elif change_24h < -1:
            sentiment = 'bearish'
            action = 'HOLD'
            confidence = 0.55
            key_factors.append(f'هبوط طفيف: {change_24h:.1f}%')
        else:
            sentiment = 'neutral'
            action = 'HOLD'
            confidence = 0.5
            key_factors.append('السوق مستقر')

        # قاعدة 2: الموقع من أعلى/أدنى 24 ساعة
        if high_24h > low_24h:
            range_position = (price - low_24h) / (high_24h - low_24h)
            if range_position > 0.9:
                risks.append('السعر قريب جداً من أعلى 24 ساعة - احتمال تصحيح')
            elif range_position < 0.1:
                key_factors.append('السعر قريب من أدنى 24 ساعة - فرصة شراء محتملة')

        # قاعدة 3: حجم التداول (إذا كان متاحاً)
        if volume_24h > 0:
            if change_24h > 2 and volume_24h > 1_000_000_000:
                key_factors.append('حجم تداول مرتفع يدعم الحركة')
            elif volume_24h < 100_000_000:
                risks.append('حجم تداول منخفض - سيولة ضعيفة')

        # صياغة السبب بالعربية
        reasoning = f"بناءً على تغير {change_24h:+.2f}% في 24 ساعة، "
        reasoning += "السوق في اتجاه " + (
            "صاعد" if sentiment == 'bullish' else
            "هابط" if sentiment == 'bearish' else
            "محايد"
        ) + ". "
        if risks:
            reasoning += "المخاطر: " + "، ".join(risks[:2])

        return MarketAnalysis(
            symbol=symbol,
            sentiment=sentiment,
            confidence=confidence,
            action=action,
            reasoning=reasoning,
            key_factors=key_factors,
            risks=risks,
            backend='rule_based',
        )


# ============================================================================
# المنسق (Manager) - يختار أفضل خلفية متاحة
# ============================================================================

class AnalyzerManager:
    """
    مدير المحللات
    ==============

    يجرب الخلفيات بالترتيب:
    1. Ollama (الأفضل - مجاني ومحلي)
    2. OpenAI (مدفوع، قوي)
    3. Rule-based (يعمل دائماً)

    مثال على الاستخدام:
    ```python
    manager = AnalyzerManager()
    result = manager.analyze('BTCUSDT', {'price': 50000, 'change_24h': 2.5})
    print(result.action, result.confidence)
    ```
    """

    def __init__(self):
        # الترتيب من الأفضل إلى الأبعد
        self.analyzers: List[BaseAnalyzer] = [
            OllamaAnalyzer(),
            OpenAIAnalyzer(),
            RuleBasedAnalyzer(),
        ]

    def analyze(self, symbol: str, market_data: Dict, context: Optional[Dict] = None) -> MarketAnalysis:
        """حلل باستخدام أول خلفية متاحة"""
        errors = []
        for analyzer in self.analyzers:
            if analyzer.is_ready():
                try:
                    result = analyzer.analyze(symbol, market_data, context)
                    return result
                except Exception as e:
                    errors.append(f"{analyzer.name}: {e}")
                    continue

        # إذا فشلت كل الخلفيات، استخدم rule-based (مضمون)
        return RuleBasedAnalyzer().analyze(symbol, market_data, context)

    def get_status(self) -> Dict:
        """حالة جميع الخلفيات"""
        return {
            'analyzers': [
                {
                    'name': a.name,
                    'available': a.is_ready(),
                } for a in self.analyzers
            ]
        }
