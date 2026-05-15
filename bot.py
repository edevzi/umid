import re
import time
import telebot
from config import (
    BOT_TOKEN, BANNED_EMOJIS, BANNED_WORDS,
    INSTANT_BAN_EMOJIS, INSTANT_BAN_WORDS, MAX_WARNINGS
)

bot = telebot.TeleBot(BOT_TOKEN)

user_warnings = {}

URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
MENTION_PATTERN = re.compile(r'@\w+')

def is_admin(message):
    if message.sender_chat:
        if message.sender_chat.id == message.chat.id:
            return True
        return False
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ['creator', 'administrator']
    except Exception:
        return False

def check_spam(text):
    if not text:
        return False, False
    text_lower = text.lower()
    
    # Check instant ban first
    for emoji in INSTANT_BAN_EMOJIS:
        if emoji in text: return True, True
    for word in INSTANT_BAN_WORDS:
        if word in text_lower: return True, True
        
    # Check regular spam
    for emoji in BANNED_EMOJIS:
        if emoji in text: return True, False
    for word in BANNED_WORDS:
        if word in text_lower: return True, False
    if URL_PATTERN.search(text): return True, False
    if MENTION_PATTERN.search(text): return True, False
    return False, False

@bot.message_handler(commands=['ban', 'del'], func=lambda message: message.chat.type in ['group', 'supergroup'])
def admin_commands(message):
    if not is_admin(message):
        return
        
    if not message.reply_to_message:
        msg = bot.reply_to(message, "Bu buyruqni spam xabarga 'Reply' qilib ishlating.")
        time.sleep(5)
        try:
            bot.delete_message(message.chat.id, msg.message_id)
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        return
        
    target_msg = message.reply_to_message
    
    if message.text.startswith('/del'):
        try:
            bot.delete_message(message.chat.id, target_msg.message_id)
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
            
    elif message.text.startswith('/ban'):
        try:
            if target_msg.sender_chat:
                bot.ban_chat_sender_chat(message.chat.id, target_msg.sender_chat.id)
            elif target_msg.from_user:
                bot.ban_chat_member(message.chat.id, target_msg.from_user.id)
                
            bot.delete_message(message.chat.id, target_msg.message_id)
            bot.delete_message(message.chat.id, message.message_id)
            warning_msg = bot.send_message(message.chat.id, "Foydalanuvchi/Kanal guruhdan bloklandi va xabari o'chirildi.")
            time.sleep(5)
            try: bot.delete_message(message.chat.id, warning_msg.message_id)
            except Exception: pass
        except Exception as e:
            bot.reply_to(message, "Xatolik yuz berdi (Botda adminlik huquqi yo'q bo'lishi mumkin).")

@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'], content_types=['text', 'photo', 'video', 'animation', 'document'])
def handle_message(message):
    if is_admin(message):
        return

    text_to_check = message.text or message.caption or ""
    
    is_spam, instant_ban = check_spam(text_to_check)
    
    if is_spam:
        chat_id = message.chat.id
        
        if message.sender_chat:
            user_id = message.sender_chat.id
            user_name = message.sender_chat.title or "Kanal"
            user_mention = f"[{user_name}](tg://user?id={user_id})"
            is_channel = True
        else:
            user_id = message.from_user.id
            user_name = message.from_user.first_name
            user_mention = f"[{user_name}](tg://user?id={user_id})"
            is_channel = False
        
        try:
            bot.delete_message(chat_id, message.message_id)
        except Exception:
            pass # Ignored to avoid terminal spam
            
        if instant_ban:
            try:
                if is_channel:
                    bot.ban_chat_sender_chat(chat_id, user_id)
                else:
                    bot.ban_chat_member(chat_id, user_id)
            except Exception:
                pass
            return
            
        key = (chat_id, user_id)
        user_warnings[key] = user_warnings.get(key, 0) + 1
        current_warnings = user_warnings[key]
            
        if current_warnings >= MAX_WARNINGS:
            try:
                if is_channel:
                    bot.ban_chat_sender_chat(chat_id, user_id)
                else:
                    bot.ban_chat_member(chat_id, user_id)
                warning_msg = bot.send_message(chat_id, f"{user_mention} qoidani ko'p marta buzgani uchun guruhdan chetlatildi.", parse_mode="Markdown")
                user_warnings[key] = 0
                time.sleep(5)
                try: bot.delete_message(chat_id, warning_msg.message_id)
                except: pass
            except Exception:
                pass
        else:
            try:
                warning_msg = bot.send_message(chat_id, f"{user_mention}, guruhda reklama tarqatma! (Ogohlantirish {current_warnings}/{MAX_WARNINGS})", parse_mode="Markdown")
                time.sleep(5)
                try: bot.delete_message(chat_id, warning_msg.message_id)
                except: pass
            except Exception:
                pass

if __name__ == "__main__":
    print("Bot started polling...")
    bot.infinity_polling()
