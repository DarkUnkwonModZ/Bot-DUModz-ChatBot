import telebot
import google.generativeai as genai
import os

# এনভায়রনমেন্ট ভেরিয়েবল থেকে টোকেন নেওয়া (নিরাপত্তার জন্য)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = 8504263842  # তোমার আইডি

# জেমিনি সেটআপ
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BOT_TOKEN)
user_chats = {}

print("বট চালু হচ্ছে...")

# অ্যাডমিন চেক ফাংশন
def is_admin(message):
    return message.from_user.id == ADMIN_ID

# /start কমান্ড
@bot.message_handler(commands=['start'])
def start(message):
    status = "অ্যাডমিন" if is_admin(message) else "ইউজার"
    bot.reply_to(message, f"হ্যালো {message.from_user.first_name}!\nআপনার স্ট্যাটাস: {status}\nআমি জেমিনি এআই। আমাকে যেকোনো প্রশ্ন করুন।")

# শুধুমাত্র অ্যাডমিনের জন্য /stats কমান্ড
@bot.message_handler(commands=['stats'])
def stats(message):
    if is_admin(message):
        bot.reply_to(message, f"বট বর্তমানে সচল আছে বন্ধু।\nঅ্যাডমিন: Dark Unknown\nইউজার সংখ্যা: {len(user_chats)}")
    else:
        bot.reply_to(message, "দুঃখিত, এই কমান্ডটি শুধুমাত্র অ্যাডমিনের জন্য।")

# মেসেজ হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def chat(message):
    user_id = message.chat.id
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])

    try:
        bot.send_chat_action(user_id, 'typing')
        response = user_chats[user_id].send_message(message.text)
        bot.reply_to(message, response.text, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "একটু সমস্যা হয়েছে, আবার চেষ্টা করুন।")

bot.infinity_polling()
