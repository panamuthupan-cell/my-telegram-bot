import telebot
import sqlite3
import random
import os
from collections import Counter
from datetime import datetime

# API Token
API_TOKEN = "8630707288:AAHc9cOnOZheSU7Brs4IzbCpdL6AsOgYAYQ"
bot = telebot.TeleBot(API_TOKEN)

# Database setup
DB_PATH = 'predictions.db'
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, number INTEGER)')
conn.commit()

# പിരീഡ് നമ്പറിനെ അടിസ്ഥാനമാക്കി കൃത്യമായ ഫലം നൽകുന്ന ഫങ്ഷൻ
def get_prediction(period_number):
    # ഒരേ പിരീഡ് നമ്പറിന് ഒരേ റിസൾട്ട് ലഭിക്കാൻ random seed ഉപയോഗിക്കുന്നു
    random.seed(str(period_number))
    
    cursor.execute("SELECT number FROM history ORDER BY id DESC LIMIT 20")
    history = [row[0] for row in cursor.fetchall()]
    
    if len(history) >= 5:
        most_common = Counter(history).most_common(1)[0][0]
        last_five_avg = sum(history[-5:]) / 5
        # സ്ഥിരതയുള്ള റിസൾട്ടിനായി ക്രമീകരണം
        return most_common if last_five_avg > 4 else random.randint(0, 4)
    return random.randint(0, 9)

@bot.message_handler(commands=['predict'])
def predict_command(message):
    # ഉപയോക്താവ് പിരീഡ് നമ്പർ നൽകണം: /predict 20260704100030151
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ ദയവായി പിരീഡ് നമ്പർ നൽകുക.\nഉദാഹരണം: /predict 20260704100030151")
            return
            
        period = parts[1]
        predicted_number = get_prediction(period)
        
        # റിസൾട്ട് കളർ ലോജിക് (Syntax Error ശരിയാക്കി)
        if predicted_number == 0: 
            color = "🔴 RED & 🟣 VIOLET"
        elif predicted_number == 5: 
            color = "🟢 GREEN & 🟣 VIOLET"
        elif predicted_number in [1, 3, 7, 9]: 
            color = "🟢 GREEN"
        elif predicted_number in [2, 4, 6, 8]: 
            color = "🔴 RED"
        else: 
            color = "🟣 VIOLET"
            
        response = (f"**PREDICTION**\n"
                    f"📊 Period: {period}\n"
                    f"🔢 Number: {predicted_number}\n"
                    f"🏆 Result: {color}\n"
                    f"⌛ Time: {datetime.now().strftime('%H:%M:%S')}")
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ ഒരു പിശക് സംഭവിച്ചു: {e}")

print("Bot started...")
bot.infinity_polling()
()

