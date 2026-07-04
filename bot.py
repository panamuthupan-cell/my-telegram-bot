import telebot
import sqlite3
import random
import os
from collections import Counter
from datetime import datetime

# API TOKEN എൻവയോൺമെന്റ് വേരിയബിളിൽ നിന്ന് എടുക്കുക
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# ഡാറ്റാബേസ് പാത്ത്
DB_PATH = '/tmp/predictions.db'
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, number INTEGER)''')
conn.commit()

def get_accurate_prediction():
    cursor.execute("SELECT number FROM history ORDER BY id DESC LIMIT 20")
    history = [row[0] for row in cursor.fetchall()]
    
    if len(history) >= 5:
        most_common = Counter(history).most_common(1)[0][0]
        last_five_avg = sum(history[:5]) / 5
        
        if last_five_avg > 4:
            prediction = random.choice([most_common, 6, 7, 8, 9])
        else:
            prediction = random.choice([most_common, 0, 1, 2, 3])
        return prediction
    
    return random.randint(0, 9)

@bot.message_handler(commands=['predict'])
def predict_command(message):
    predicted_number = get_accurate_prediction()
    
    # കളർ ലോജിക് പൂർണ്ണരൂപം
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

    response = (
        f"📊 **PREDICTION**\n"
        f"🔢 Number: {predicted_number}\n"
        f"🔻 Result: {color}\n"
        f"⏳ Time: {datetime.now().strftime('%H:%M:%S')}"
    )
    bot.reply_to(message, response)

@bot.message_handler(commands=['add'])
def add_number(message):
    try:
        parts = message.text.split()
        num = int(parts[1])
        if 0 <= num <= 9:
            cursor.execute("INSERT INTO history (number) VALUES (?)", (num,))
            conn.commit()
            bot.reply_to(message, f"✅ {num} സേവ് ചെയ്തു.")
        else:
            bot.reply_to(message, "⚠️ 0-9 നമ്പറുകൾ മാത്രം.")
    except Exception as e:
        bot.reply_to(message, "❌ തെറ്റായ ഫോർമാറ്റ്. /add [number] എന്ന് ഉപയോഗിക്കുക.")

print("Bot started...")
bot.infinity_polling()
