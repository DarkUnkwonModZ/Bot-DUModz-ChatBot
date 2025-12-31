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

# সেফটি সেটিংস
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# মডেল লোড করার ফাংশন (Error ফিক্সিং লজিকসহ)
def load_model():
    # এই লিস্টের মডেলগুলো এক এক করে ট্রাই করবে যেটা কাজ করে
    model_names = [
        "gemini-1.5-flash", 
        "models/gemini-1.5-flash", 
        "gemini-1.5-pro", 
        "gemini-pro"
    ]
    
    for name in model_names:
        try:
            print(f"চেষ্টা করছি মডেল: {name}")
            m = genai.GenerativeModel(model_name=name, safety_settings=safety_settings)
            # চেক করার জন্য একটি ছোট টেস্ট জেনারেট করা
            m.generate_content("Hi") 
            print(f"সফলভাবে কানেক্ট হয়েছে: {name}")
            return m
        except Exception as e:
            print(f"{name} কাজ করেনি। কারণ: {e}")
            continue
    return None

# মডেল সেটআপ
model = load_model()

bot = telebot.TeleBot(BOT_TOKEN)
user_chats = {}

print("বট সচল হচ্ছে...")

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    if model is None:
        bot.reply_to(message, "⚠️ এআই মডেল লোড করা যায়নি। আপনার API Key চেক করুন।")
    else:
        status = "অ্যাডমিন" if message.from_user.id == ADMIN_ID else "ইউজার"
        bot.reply_to(message, f"হ্যালো {name}!\nআপনার স্ট্যাটাস: {status}\nআমি এখন অনলাইনে আছি। প্রশ্ন করুন!")

@bot.message_handler(func=lambda message: True)
def chat_handler(message):
    user_id = message.chat.id
    
    if model is None:
        bot.reply_to(message, "দুঃখিত, এআই সার্ভার ডাউন।")
        return

    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])

    try:
        bot.send_chat_action(user_id, 'typing')
        chat = user_chats[user_id]
        response = chat.send_message(message.text)
        
        if response.text:
            bot.reply_to(message, response.text, parse_mode="Markdown")
        else:
            bot.reply_to(message, "বট উত্তর দিতে পারছে না।")

    except Exception as e:
        print(f"Error: {traceback.format_exc()}")
        if user_id == ADMIN_ID:
            bot.reply_to(message, f"❌ সমস্যা: `{str(e)}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "একটু সমস্যা হয়েছে বন্ধু, আবার চেষ্টা করো।")

bot.infinity_polling()
