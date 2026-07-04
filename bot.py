import telebot
import sqlite3
import random
from collections import Counter
from datetime import datetime
import os

# API TOKEN എൻവയോൺമെന്റ് വേരിയബിളിൽ നിന്ന് എടുക്കുന്നതാണ് ഏറ്റവും സുരക്ഷിതം
API_TOKEN = os.getenv("API_TOKEN", "YOUR_API_TOKEN_HERE")
bot = telebot.TeleBot(API_TOKEN)

# Render/Cloud പ്ലാറ്റ്‌ഫോമിൽ ഡാറ്റാബേസ് ഫയൽ ക്രാഷ് ആവാതിരിക്കാൻ 
# persistent storage ഉള്ള ഫോൾഡറിൽ വേണം ഡാറ്റാബേസ് സേവ് ചെയ്യാൻ.
# ഇവിടെ ലളിതമായി നിലവിലെ ഫോൾഡറിൽ തന്നെ സേവ് ചെയ്യുന്നു.
conn = sqlite3.connect('predictions.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, number INTEGER)''')
conn.commit()

def get_accurate_prediction():
    # ഹിസ്റ്ററിയിൽ നിന്ന് ഡാറ്റ എടുക്കുന്നു
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
    
    if predicted_number == 0: color = "🔴 RED & 🟣 VIOLET"
    elif predicted_number == 5: color = "🟢 GREEN & 🟣 VIOLET"
    elif predicted_number in [1, 3, 7, 9]: color = "🟢 GREEN"
    elif predicted_number in [2, 4, 6, 8]: color = "🔴 RED"
    else: color = "🟣 VIOLET"

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
        if len(parts) < 2:
            raise ValueError
        num = int(parts[1])
