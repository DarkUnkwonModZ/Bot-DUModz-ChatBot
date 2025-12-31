import telebot
import google.generativeai as genai
import os
import traceback

# এনভায়রনমেন্ট ভেরিয়েবল
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = 8504263842

# জেমিনি এআই কনফিগারেশন
genai.configure(api_key=GEMINI_API_KEY)

# সেফটি সেটিংস (যাতে কোনো উত্তর ব্লক না হয়)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=safety_settings
)

bot = telebot.TeleBot(BOT_TOKEN)
user_chats = {}

print("বট সচল হচ্ছে...")

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    status = "অ্যাডমিন" if message.from_user.id == ADMIN_ID else "ইউজার"
    bot.reply_to(message, f"হ্যালো {name}!\nআপনার স্ট্যাটাস: {status}\nআমি জেমিনি এআই। আপনি এখন আমার সাথে চ্যাট করতে পারেন।")

@bot.message_handler(func=lambda message: True)
def chat_handler(message):
    user_id = message.chat.id
    
    # চ্যাট সেশন শুরু বা রিকল
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])

    try:
        bot.send_chat_action(user_id, 'typing')
        
        # জেমিনি থেকে রেসপন্স জেনারেট
        chat = user_chats[user_id]
        response = chat.send_message(message.text)
        
        # উত্তর পাঠানো
        if response.text:
            bot.reply_to(message, response.text, parse_mode="Markdown")
        else:
            bot.reply_to(message, "বট কোনো উত্তর তৈরি করতে পারেনি।")

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error: {error_details}")
        
        # শুধুমাত্র অ্যাডমিনকে এরর মেসেজ পাঠানো যাতে ফিক্স করা যায়
        if user_id == ADMIN_ID:
            bot.reply_to(message, f"❌ এরর ডিটেইলস (অ্যাডমিন ভিউ):\n`{str(e)}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "দুঃখিত বন্ধু, একটু কারিগরি সমস্যা হয়েছে। অ্যাডমিনকে জানানো হয়েছে।")

bot.infinity_polling()
