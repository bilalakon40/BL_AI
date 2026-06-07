"""
مسارات API للذكاء الاصطناعي
============================

يوفر نقاط نهاية (endpoints) لاستخدام محلل AI للسوق.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from app.ai.analyzer import AnalyzerManager, MarketAnalysis


router = APIRouter()
manager = AnalyzerManager()


class AnalyzeRequest(BaseModel):
    """طلب تحليل السوق"""
    symbol: str                              # مثل "BTCUSDT"
    market_data: Dict                        # البيانات: price, change_24h, etc
    context: Optional[Dict] = None           # معلومات إضافية (أخبار)


class BatchAnalyzeRequest(BaseModel):
    """طلب تحليل عدة عملات دفعة واحدة"""
    symbols: List[str]
    market_data: Dict[str, Dict]              # {symbol: data}


@router.get('/ai/status')
async def ai_status():
    """
    حالة جميع الخلفيات المتاحة
    ===========================
    يُرجع ما هي المحللات الجاهزة للاستخدام
    """
    return manager.get_status()


@router.post('/ai/analyze', response_model=Dict)
async def analyze_market(req: AnalyzeRequest):
    """
    حلل السوق لـ عملة واحدة
    ========================

    يستخدم أول خلفية متاحة (Ollama → OpenAI → Rule-based)

    المدخلات:
    - symbol: اسم العملة
    - market_data: بيانات السوق
    - context: (اختياري) معلومات إضافية

    المخرجات:
    - sentiment, action, confidence, reasoning
    """
    try:
        result = manager.analyze(req.symbol, req.market_data, req.context)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(500, f'فشل التحليل: {str(e)}')


@router.post('/ai/analyze-batch')
async def analyze_batch(req: BatchAnalyzeRequest):
    """
    حلل عدة عملات دفعة واحدة
    """
    results = []
    for symbol in req.symbols:
        data = req.market_data.get(symbol, {'price': 0, 'change_24h': 0})
        try:
            result = manager.analyze(symbol, data)
            results.append(result.to_dict())
        except Exception as e:
            results.append({
                'symbol': symbol,
                'error': str(e),
            })
    return {'results': results, 'count': len(results)}
