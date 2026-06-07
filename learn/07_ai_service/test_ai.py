"""
اختبار سريع لمحلل AI
====================

يجرب جميع نقاط النهاية (endpoints) الخاصة بالـ AI.

الاستخدام:
1. شغّل الخادم في terminal آخر:
   cd D:\bilal AI\BL_AI\backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

2. في terminal جديد، شغّل هذا السكريبت:
   python test_ai.py
"""

import httpx
import json
import sys

BASE = 'http://127.0.0.1:8000/api'


def test_status():
    """حالة الخلفيات المتاحة"""
    print('=' * 60)
    print('1. حالة الخلفيات (/api/ai/status)')
    print('=' * 60)
    r = httpx.get(f'{BASE}/ai/status', timeout=10)
    print(f'Status: {r.status_code}')
    data = r.json()
    for a in data['analyzers']:
        icon = '✓' if a['available'] else '✗'
        print(f"  {icon} {a['name']}")
    print()


def test_analyze():
    """تحليل عملة واحدة"""
    print('=' * 60)
    print('2. تحليل عملة واحدة (/api/ai/analyze)')
    print('=' * 60)
    samples = [
        ('BTCUSDT', {'price': 50000, 'change_24h': -8.0, 'volume_24h': 2_000_000_000, 'high_24h': 55000, 'low_24h': 48000}),
        ('ETHUSDT', {'price': 3000, 'change_24h': 0.5, 'volume_24h': 800_000_000, 'high_24h': 3050, 'low_24h': 2950}),
        ('SOLUSDT', {'price': 150, 'change_24h': 6.0, 'volume_24h': 300_000_000, 'high_24h': 155, 'low_24h': 140}),
    ]
    for symbol, data in samples:
        r = httpx.post(f'{BASE}/ai/analyze', json={'symbol': symbol, 'market_data': data}, timeout=10)
        result = r.json()
        print(f"\n{symbol}: {result['sentiment']:8s} -> {result['action']:4s} (conf: {result['confidence']:.0%})")
        print(f"  السبب: {result['reasoning']}")
        if result['key_factors']:
            print(f"  عوامل: {', '.join(result['key_factors'][:2])}")
    print()


def test_batch():
    """تحليل عدة عملات دفعة"""
    print('=' * 60)
    print('3. تحليل دفعة (/api/ai/analyze-batch)')
    print('=' * 60)
    body = {
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT'],
        'market_data': {
            'BTCUSDT': {'price': 50000, 'change_24h': 2.5, 'volume_24h': 1500000000, 'high_24h': 51000, 'low_24h': 49000},
            'ETHUSDT': {'price': 2500, 'change_24h': -3.5, 'volume_24h': 800000000, 'high_24h': 2600, 'low_24h': 2400},
            'SOLUSDT': {'price': 100, 'change_24h': 0.0, 'volume_24h': 200000000, 'high_24h': 102, 'low_24h': 98},
            'BNBUSDT': {'price': 600, 'change_24h': -8.0, 'volume_24h': 500000000, 'high_24h': 660, 'low_24h': 580},
        }
    }
    r = httpx.post(f'{BASE}/ai/analyze-batch', json=body, timeout=20)
    data = r.json()
    print(f"عدد التحليلات: {data['count']}\n")
    for item in data['results']:
        print(f"  {item['symbol']:10s}: {item['sentiment']:8s} -> {item['action']:4s} (conf: {item['confidence']:.0%})")
    print()


if __name__ == '__main__':
    try:
        test_status()
        test_analyze()
        test_batch()
        print('=' * 60)
        print('جميع الاختبارات نجحت! ✓')
        print('=' * 60)
    except httpx.ConnectError:
        print('خطأ: لا يمكن الاتصال بالخادم')
        print('تأكد من تشغيله في terminal آخر:')
        print('  cd D:\\bilal AI\\BL_AI\\backend')
        print('  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000')
        sys.exit(1)
    except Exception as e:
        print(f'خطأ: {e}')
        sys.exit(1)
