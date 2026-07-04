import telebot
import sqlite3
import random
from collections import Counter
from datetime import datetime

API_TOKEN = "YOUR_API_TOKEN_HERE"
bot = telebot.TeleBot(API_TOKEN)

# ഡാറ്റാബേസ് കണക്ഷൻ
conn = sqlite3.connect('predictions.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, number INTEGER)''')
conn.commit()

def get_accurate_prediction():
    # അവസാനത്തെ 20 എൻട്രികൾ എടുക്കുന്നു
    history = [row[0] for row in cursor.execute("SELECT number FROM history ORDER BY id DESC LIMIT 20").fetchall()]
    
    if len(history) >= 10:
        # 1. Frequency Logic: കൂടുതൽ തവണ വന്ന നമ്പർ കണ്ടെത്തുന്നു
        most_common = Counter(history).most_common(1)[0][0]
        
        # 2. Moving Average Logic: അവസാന 5 നമ്പറുകളുടെ ആവറേജ് എടുക്കുന്നു
        last_five_avg = sum(history[:5]) / 5
        
        # ഇവ രണ്ടും വെച്ച് ഒരു പ്രെഡിക്ഷൻ
        if last_five_avg > 4:
            prediction = random.choice([most_common, 6, 7, 8, 9])
        else:
            prediction = random.choice([most_common, 0, 1, 2, 3])
        return prediction
    
    return random.randint(0, 9)

@bot.message_handler(commands=['predict'])
def predict_command(message):
    predicted_number = get_accurate_prediction()
    
    # കളർ ലോജിക്
    if predicted_number == 0: color = "🔴 RED & 🟣 VIOLET"
    elif predicted_number == 5: color = "🟢 GREEN & 🟣 VIOLET"
    elif predicted_number in [1, 3, 7, 9]: color = "🟢 GREEN"
    elif predicted_number in [2, 4, 6, 8]: color = "🔴 RED"
    else: color = "🟣 VIOLET" # Default case

    response = (
        f"📊 **PREDICTION**\n"
        f"🔢 Number: {predicted_number}\n"
        f"🔻 Result: {color}\n"
        f"⏳ Time: {datetime.now().strftime('%H:%M:%S')}"
    )
    bot.reply_to(message, response)

# ഹിസ്റ്ററിയിൽ പുതിയ നമ്പർ ചേർക്കാൻ ഒരു കമാൻഡ് (ഇത് വളരെ പ്രധാനമാണ്)
@bot.message_handler(commands=['add'])
def add_number(message):
    try:
        num = int(message.text.split()[1])
        cursor.execute("INSERT INTO history (number) VALUES (?)", (num,))
        conn.commit()
        bot.reply_to(message, f"✅ നമ്പർ {num} സേവ് ചെയ്തു.")
    except:
        bot.reply_to(message, "❌ തെറ്റായ ഫോർമാറ്റ്. /add [number] എന്ന് ഉപയോഗിക്കുക.")

bot.polling(none_stop=True)

