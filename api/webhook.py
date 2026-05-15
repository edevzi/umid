import os
import sys
import telebot
from flask import Flask, request, Response

# Loyiha papkasini yo'lga qo'shish (Vercel importlarda adashmasligi uchun)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import bot
from config import BOT_TOKEN

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Bot is running on Vercel!", 200

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return Response('OK', status=200)
    else:
        return Response('Forbidden', status=403)

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    host_url = request.host_url.replace("http://", "https://")
    webhook_url = f"{host_url}{BOT_TOKEN}"
    
    bot.remove_webhook()
    s = bot.set_webhook(url=webhook_url)
    if s:
        return f"Webhook muvaffaqiyatli o'rnatildi:\n{webhook_url}", 200
    else:
        return "Webhook o'rnatishda xatolik yuz berdi.", 400
