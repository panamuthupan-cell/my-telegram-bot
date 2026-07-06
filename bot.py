import logging
import random
from datetime import datetime, timezone
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.request import HTTPXRequest

# ലോഗിംഗ് സെറ്റപ്പ്
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

TOKEN = "8891642391:AAGT9kZ9MUUvi29DjrHRGju8CKLCtmuSdhA" 
CHAT_ID = "-100XXXXXXXXXX" # നിങ്ങളുടെ ഗ്രൂപ്പ് ഐഡി ഇവിടെ നൽകുക

# ഈ OFFSET വാല്യൂ ആണ് നിങ്ങളുടെ പീരിയഡ് ശരിയാക്കേണ്ടത്.
# ഗെയിമിലെ പീരിയഡ് - ബോട്ടിലെ പീരിയഡ് = വ്യത്യാസം. 
# ആ വ്യത്യാസം ഇവിടെ നൽകുക. 
PERIOD_OFFSET = 625 

def get_current_period():
    now = datetime.now(timezone.utc)
    # ഗെയിമിന്റെ ഫോർമാറ്റ് അനുസരിച്ച് പീരിയഡ് കണക്കാക്കുന്നു
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
    application = ApplicationBuilder().token(TOKEN).request(HTTPXRequest(connect_timeout=60.0)).build()
    application.add_handler(CommandHandler("predict", predict_command))
    print("Bot Running...")
    application.run_polling()
