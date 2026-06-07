# الدرس 01: أول برنامج Python

# 1. أبسط أمر: print() - للطباعة على الشاشة
print("مرحباً يا بلال!")
print("=" * 50)

# 2. المتغيرات (Variables) - صناديق نخزن فيها قيم
name = "بلال"
age = 25
city = "ليبيا"
balance = 1000.50
is_active = True

# 3. طباعة المتغيرات
print("الاسم:", name)
print("العمر:", age)
print("المدينة:", city)
print("الرصيد:", balance)
print("نشط:", is_active)
print("=" * 50)

# 4. العمليات الحسابية
price_btc = 50000
amount = 0.05
total = price_btc * amount
print(f"سعر البيتكوين: ${price_btc}")
print(f"الكمية: {amount} BTC")
print(f"الإجمالي: ${total}")
print("=" * 50)

# 5. أنواع البيانات (Data Types)
print("أنواع البيانات:")
print(f"  الاسم - str:    '{name}'")
print(f"  العمر - int:    {age}")
print(f"  الرصيد - float: {balance}")
print(f"  نشط - bool:     {is_active}")
print("=" * 50)

# 6. الإدخال من المستخدم (input)
print("\nجرّب بنفسك!")
user_name = input("ما اسمك؟ ")
print(f"أهلاً {user_name}! سعيد بتعلمك Python")

user_age = input("كم عمرك؟ ")
print(f"عمرك {user_age} سنة. بعد 5 سنوات سيكون عمرك {int(user_age) + 5}")
