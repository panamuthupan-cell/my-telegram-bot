
import logging
import random
import threading
import os
from flask import Flask
from datetime import datetime, timezone
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.request import HTTPXRequest

# ലോഗിംഗ് സെറ്റപ്പ്
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

TOKEN = "8891642391:AAGT9kZ9MUUvi29DjrHRGju8CKLCtmuSdhA" 

# Flask ആപ്പ് സെറ്റപ്പ്
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # Render നൽകുന്ന PORT ഉപയോഗിക്കുന്നു, അല്ലെങ്കിൽ ഡിഫോൾട്ട് 10000
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# പീരിയഡ് കണക്കാക്കുന്ന ഫംഗ്ഷൻ
PERIOD_OFFSET = 625 
def get_current_period():
    now = datetime.now(timezone.utc)
    base_period = int(now.strftime("%Y%m%d100010000"))
    minutes = now.hour * 60 + now.minute
    return base_period + minutes - PERIOD_OFFSET

def get_prediction(period):
    random.seed(period)
    number = random.randint(0, 9)
    result = "Small" if number <= 4 else "Big"
    return number, result

async def predict_command(update, context):
    period = get_current_period()
    num, res = get_prediction(period)
    await update.message.reply_text(f"🎯 Period: {period}\n🎯 Number: {num}\n🎯 Result: {res}")

if __name__ == '__main__':
    # Flask സെർവർ മറ്റൊരു ത്രെഡിൽ റൺ ചെയ്യുന്നു
    threading.Thread(target=run_flask).start()
    
    application = ApplicationBuilder().token(TOKEN).request(HTTPXRequest(connect_timeout=60.0)).build()
    application.add_handler(CommandHandler("predict", predict_command))
    print("Bot Running...")
    application.run_polling()
