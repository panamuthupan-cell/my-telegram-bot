import logging
import random
import threading
from datetime import datetime, timezone
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.request import HTTPXRequest

# ലോഗിംഗ് സെറ്റപ്പ്
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# ടോക്കൺ
TOKEN = "8891642391:AAGT9kZ9MUUvi29DjrHRGju8CKLCtmuSdhA" 
PERIOD_OFFSET = 625 

# Flask സെർവർ സെറ്റപ്പ്
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

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
    try:
        period = get_current_period()
        num, res = get_prediction(period)
        await update.message.reply_text(f"🎯 Period: {period}\n🎯 Number: {num}\n🎯 Result: {res}")
    except Exception as e:
        logging.error(f"Error in predict_command: {e}")

if __name__ == '__main__':
    # Flask വെബ് സെർവർ സ്റ്റാർട്ട് ചെയ്യുന്നു
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # Telegram ബോട്ട് സെറ്റപ്പ്
    request = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0)
    application = ApplicationBuilder().token(TOKEN).request(request).build()
    
    application.add_handler(CommandHandler("predict", predict_command))
    
    print("Bot and Web Server Running...")
    
    # ബോട്ട് റൺ ചെയ്യുന്നു
    application.run_polling()
