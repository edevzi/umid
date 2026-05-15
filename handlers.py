import re
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from config import BANNED_EMOJIS, BANNED_WORDS, MAX_WARNINGS, INSTANT_BAN_EMOJIS, INSTANT_BAN_WORDS

router = Router()

# Dictionary to keep track of user warnings: {(chat_id, user_id): count}
user_warnings = {}

# Regex for detecting URLs and Mentions
URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
MENTION_PATTERN = re.compile(r'@\w+')

async def is_admin(message: Message, bot: Bot) -> bool:
    # If the message is sent on behalf of a channel or anonymously as the group
    if message.sender_chat:
        if message.sender_chat.id == message.chat.id:
            return True
        return False
        
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ['creator', 'administrator']
    except Exception:
        return False

def check_spam(text: str) -> tuple[bool, bool]:
    if not text:
        return False, False
        
    text_lower = text.lower()
    
    # Check instant ban emojis
    for emoji in INSTANT_BAN_EMOJIS:
        if emoji in text:
            return True, True
            
    # Check instant ban words
    for word in INSTANT_BAN_WORDS:
        if word in text_lower:
            return True, True
    
    # Check emojis
    for emoji in BANNED_EMOJIS:
        if emoji in text:
            return True, False
            
    # Check banned words
    for word in BANNED_WORDS:
        if word in text_lower:
            return True, False
            
    # Check URLs
    if URL_PATTERN.search(text):
        return True, False
        
    # Check Mentions
    if MENTION_PATTERN.search(text):
        return True, False
        
    return False, False

@router.message(F.text.startswith('/ban') | F.text.startswith('/del'))
async def admin_commands(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return
        
    if not message.reply_to_message:
        msg = await message.reply("Bu buyruqni spam xabarga 'Reply' qilib ishlating.")
        await asyncio.sleep(5)
        try:
            await msg.delete()
            await message.delete()
        except TelegramBadRequest:
            pass
        return
        
    target_msg = message.reply_to_message
    
    if message.text.startswith('/del'):
        try:
            await target_msg.delete()
            await message.delete()
        except TelegramBadRequest:
            pass
            
    elif message.text.startswith('/ban'):
        try:
            if target_msg.sender_chat:
                await bot.ban_chat_sender_chat(message.chat.id, target_msg.sender_chat.id)
            elif target_msg.from_user:
                await bot.ban_chat_member(message.chat.id, target_msg.from_user.id)
            
            await target_msg.delete()
            await message.delete()
            warning_msg = await message.answer("Foydalanuvchi/Kanal guruhdan bloklandi va xabari o'chirildi.")
            await asyncio.sleep(5)
            try:
                await warning_msg.delete()
            except TelegramBadRequest:
                pass
        except TelegramBadRequest:
            await message.reply("Xatolik yuz berdi (Botda adminlik huquqi yo'q bo'lishi mumkin).")

@router.message()
async def moderate_messages(message: Message, bot: Bot):
    # Only moderate in groups/supergroups
    if message.chat.type not in ['group', 'supergroup']:
        return

    # Check if user is admin or it's a channel post
    if await is_admin(message, bot):
        return

    text_to_check = message.text or message.caption or ""
    
    is_spam, is_instant_ban = check_spam(text_to_check)
    
    if is_spam:
        chat_id = message.chat.id
        
        # Determine sender ID and name
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
            
        # Delete the message
        try:
            await message.delete()
        except TelegramBadRequest:
            pass # Bot might not have permission to delete
            
        if is_instant_ban:
            try:
                if is_channel:
                    await bot.ban_chat_sender_chat(chat_id, user_id)
                else:
                    await bot.ban_chat_member(chat_id, user_id)
                    
                warning_msg = await message.answer(f"{user_mention} qat'iy taqiqlangan so'z/smayldan foydalangani uchun guruhdan chetlatildi.", parse_mode="Markdown")
                await asyncio.sleep(5)
                try:
                    await warning_msg.delete()
                except TelegramBadRequest:
                    pass
            except TelegramBadRequest:
                pass
            return
            
        # Increment warning count
        key = (chat_id, user_id)
        user_warnings[key] = user_warnings.get(key, 0) + 1
        current_warnings = user_warnings[key]
        
        if current_warnings >= MAX_WARNINGS:
            try:
                if is_channel:
                    await bot.ban_chat_sender_chat(chat_id, user_id)
                else:
                    await bot.ban_chat_member(chat_id, user_id)
                    
                warning_msg = await message.answer(f"{user_mention} qoidani ko'p marta buzgani uchun guruhdan chetlatildi.", parse_mode="Markdown")
                user_warnings[key] = 0 # Reset warnings
                await asyncio.sleep(5)
                try:
                    await warning_msg.delete()
                except TelegramBadRequest:
                    pass
            except TelegramBadRequest:
                pass
        else:
            # Send warning message
            warning_msg = await message.answer(
                f"{user_mention}, guruhda reklama tarqatma! (Ogohlantirish {current_warnings}/{MAX_WARNINGS})",
                parse_mode="Markdown"
            )
            
            # Delete the warning message after a few seconds to avoid clutter
            await asyncio.sleep(5)
            try:
                await warning_msg.delete()
            except TelegramBadRequest:
                pass
