import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. إعداد خادم Web لإبقاء البوت حياً 24/7 على Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. بيانات البوت والقناة الخاصة بك ---
TOKEN = '8936817987:AAH5dGFi9q9VFWr3VUR_pHJA-NtyXCNTvOQ'
CHANNEL_USERNAME = '@shbin4'

bot = telebot.TeleBot(TOKEN)

# دالة التحقق من اشتراك المستخدم في القناة
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"خطأ في التحقق من الاشتراك: {e}")
        return False

# معالج الرسائل
@bot.message_handler(func=lambda message: True)
def enforce_subscription(message):
    user_id = message.from_user.id
    
    # إذا كان المستخدم مشتركاً في القناة
    if check_subscription(user_id):
        if message.text == '/start':
            bot.reply_to(message, "أهلاً بك! أنت مشترك بالقناة ويمكنك استخدام البوت الآن 🚀")
    else:
        # إذا لم يكن مشتركاً، حذف الرسالة (في المجموعات) وإرسال التنبيه
        try:
            if message.chat.type in ['group', 'supergroup']:
                bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass

        # إنشاء زر الانتقال للقناة
        markup = InlineKeyboardMarkup()
        channel_url = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
        btn = InlineKeyboardButton("📢 اضغط هنا للاشتراك في القناة", url=channel_url)
        markup.add(btn)

        bot.send_message(
            message.chat.id,
            f"عذراً يا {message.from_user.first_name}!\nعليك الاشتراك في القناة أولاً لتتمكن من إرسال الرسائل.",
            reply_markup=markup
        )

# --- 3. تشغيل الخادم والبوت ---
if __name__ == '__main__':
    keep_alive()
    print("تم تشغيل البوت بنجاح...")
    bot.infinity_polling(skip_pending=True)
