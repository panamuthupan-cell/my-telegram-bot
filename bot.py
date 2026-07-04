import telebot
import sqlite3
import random
import os
from collections import Counter
from datetime import datetime
import sys

# API Token
API_TOKEN = "8630707288:AAHc9cOnOZheSU7Brs4IzbCpdL6AsOgYAYQ"
# ടോക്കൺ ലൈനിന് തൊട്ടുതാഴെ ഇത് ചേർക്കുക

# ടോക്കൺ പരിശോധന
if not API_TOKEN:
    print("Error: API_TOKEN സെറ്റ് ചെയ്തിട്ടില്ല!")
    sys.exit()

bot = telebot.TeleBot(API_TOKEN)
# ടോക്കൺ ലൈനിന് തൊട്ടുതാഴെ ഇത് ചേർക്കുക
print(f"Bot connected to: {bot.get_me().first_name}")

# Database setup
DB_PATH = 'predictions.db'
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, number INTEGER)')
conn.commit()

# Prediction logic
def get_accurate_prediction():
    cursor.execute("SELECT number FROM history ORDER BY id DESC LIMIT 20")
    history = [row[0] for row in cursor.fetchall()]
    if len(history) >= 5:
        most_common = Counter(history).most_common(1)[0][0]
        last_five_avg = sum(history[-5:]) / 5
        return random.choice([most_common, 6, 7, 8, 9]) if last_five_avg > 4 else random.choice([most_common, 0, 1, 2, 3])
    return random.randint(0, 9)

# Bot Handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "സ്വാഗതം! /predict എന്ന് ടൈപ്പ് ചെയ്യുക.")

@bot.message_handler(commands=['predict'])
def predict_command(message):
    predicted_number = get_accurate_prediction()
    if predicted_number == 0: color = "🔴 RED & 🟣 VIOLET"
    elif predicted_number == 5: color = "🟢 GREEN & 🟣 VIOLET"
    elif predicted_number in [1, 3, 7, 9]: color = "🟢 GREEN"
    elif predicted_number in [2, 4, 6, 8]: color = "🔴 RED"
    else: color = "🟣 VIOLET"
    
    response = (f"**PREDICTION**\n📊 Number: {predicted_number}\n🏆 Result: {color}\n⌛ Time: {datetime.now().strftime('%H:%M:%S')}")
    bot.reply_to(message, response)

@bot.message_handler(commands=['add'])
def add_number(message):
    try:
        parts = message.text.split()
        num = int(parts[1])
        cursor.execute("INSERT INTO history (number) VALUES (?)", (num,))
        conn.commit()
        bot.reply_to(message, f"✅ {num} സേവ് ചെയ്തു.")
    except:
        bot.reply_to(message, "❌ തെറ്റായ ഫോർമാറ്റ്.")

# Bot Polling
print("Bot started...")
try:
    bot.infinity_polling()
except Exception as e:
    print(f"പ്രശ്നം ഇതാണ്: {e}")

