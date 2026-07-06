import logging
import random
import time
from datetime import datetime, timezone
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.request import HTTPXRequest

# ലോഗിംഗ് സെറ്റപ്പ്
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# നിങ്ങളുടെ ബോട്ട് ടോക്കൺ ഇവിടെ നൽകുക (പഴയത് Revoke ചെയ്ത ശേഷം മാത്രം)
TOKEN = "8891642391:AAGT9kZ9MUUvi29DjrHRGju8CKLCtmuSdhA" 
CHAT_ID = "-100XXXXXXXXXX" 

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
    try:
        period = get_current_period()
        num, res = get_prediction(period)
        await update.message.reply_text(f"🎯 Period: {period}\n🎯 Number: {num}\n🎯 Result: {res}")
    except Exception as e:
        logging.error(f"Error in predict_command: {e}")

if __name__ == '__main__':
    # HTTPXRequest ഉപയോഗിച്ച് ടൈംഔട്ട് സെറ്റ് ചെയ്യുന്നു
    request = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0)
    application = ApplicationBuilder().token(TOKEN).request(request).build()
    
    application.add_handler(CommandHandler("predict", predict_command))
    
    print("Bot Running...")
    
    # ബോട്ട് ക്രാഷ് ആയാലും വീണ്ടും റൺ ചെയ്യാൻ ഒരു ലൂപ്പ്
    while True:
        try:
            application.run_polling()
        except Exception as e:
            logging.error(f"Bot Crashed: {e}. Restarting in 5 seconds...")
            time.sleep(5) # 5 സെക്കൻഡിന് ശേഷം റീസ്റ്റാർട്ട് ചെയ്യും
