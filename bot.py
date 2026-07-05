import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import random
import time

TOKEN = "8666369696:AAES2XoCOLW8lhKE_SbY_u2MVGAkOl0yEi4"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # നിലവിലെ സമയത്തെ അടിസ്ഥാനമാക്കി ഒരു 'സീഡ്' ഉണ്ടാക്കുന്നു. 
    # ഇത് ചെറിയ സമയവ്യത്യാസത്തിൽ ഒരേ ഫലം നൽകാൻ സഹായിക്കും.
    fixed_seed = int(time.time() // 10) 
    random.seed(fixed_seed)
    
    number = random.randint(0, 9)
    
    if number <= 4:
        result_type = "Small"
    else:
        result_type = "Big"
    
    response = f"🎯 Prediction (Period based):\nNumber: {number}\nResult: {result_type}"
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    predict_handler = CommandHandler('predict', predict)
    application.add_handler(predict_handler)
    print("Bot is running...")
    application.run_polling()

