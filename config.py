import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Spam patterns and emojis (ogohlantirish + 3 martadan keyin ban)
BANNED_EMOJIS = ["💋", "❤️"]
BANNED_WORDS = [
    "profilimda kutaman",
    "profilimga qarang",
    "kirib ko'ring",
    "profilimga kirib ko'ring",
    "salom, mening profilimga",
    "profilimni bir ko'ring",
    "profilim",
    "18+",
    "porn",
    "ehtiros",
    "extiros",
    "uyatsiz",
    "uyatsizvideo",
    "seks",
    "seksvideo",
    "sex",
    "sexvideo",
    "botga kir"
]

# Instant ban patterns (darhol ban, ogohlantirish yo'q)
INSTANT_BAN_EMOJIS = ["😘", "😏", "🍌", "🍑", "🕊"]
INSTANT_BAN_WORDS = [
    "profilimga o'ting",
    "profilimga kiring",
    "profilimni bir ko'ring",
    "zavqlaning",
    "pushaymon bo'lmaysiz",
    "pushaymon",
    "pashimon bo'lmaysiz",
    "pashimon",
    "hayratda qoling",
    "afsuslanmaysiz",
    "загляните в мой профиль",
    "посмотрите мой профиль",
    "заходи в профиль",
    "мой профиль",
    "в мой профиль"
]

MAX_WARNINGS = 3
