# Telegram Spam-Filter Bot

Telegram guruhlaridagi har xil spamlarni ushlab va o'chirib tashlaydigan administrator bot.

## Xususiyatlari
- 🚫 Barcha reklama va nojo'ya so'zlarni avtomatik o'chirish
- 🚨 Spammerlarni guruhdan chetlatish (Ban)
- 📢 Kanal nomidan guruhda yozuvchi bot/kanallarni ham bloklash
- 👮‍♂️ `/del` va `/ban` admin buyruqlari

## Serverga o'rnatish

Serverda loyihani ishga tushirish uchun Docker va Docker Compose o'rnatilgan bo'lishi kerak.

1. Loyihani yuklab oling:
```bash
git clone <sizning-github-repo-havolangiz>
cd Spambot
```

2. Muhit o'zgaruvchilari faylini yarating:
`.env` nomli fayl yarating va uning ichiga o'zingizning bot tokeningizni yozing:
```
BOT_TOKEN=123456789:AAH...
```

3. Docker orqali ishga tushiring:
```bash
docker-compose up -d
```

Bot fonda (background) uzluksiz ishlay boshlaydi. Uni to'xtatish uchun:
```bash
docker-compose down
```

## Diqqat!
Bot barcha amallarni to'g'ri bajarishi uchun guruhda unga **"Delete Messages"** va **"Ban Users"** adminlik huquqlarini berishni unutmang.
