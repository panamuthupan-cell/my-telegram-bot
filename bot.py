import logging
import random
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from flask import Flask
from threading import Thread

# OCR ലൈബ്രറികൾ - പിശക് ഒഴിവാക്കാൻ try-except ഉപയോഗിക്കുന്നു
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is active!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

TOKEN = "8666369696:AAES2XoCOLW8lhKE_SbY_u2MVGAkOl0yEi4"
period_data = {}

async def handle_photo(update, context):
    if not HAS_OCR:
        await update.message.reply_text("OCR ലൈബ്രറി ഇൻസ്റ്റാൾ ചെയ്തിട്ടില്ല.")
        return

    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("temp.jpg")
    
    text = pytesseract.image_to_string(Image.open("temp.jpg"))
    period_id = "".join(filter(str.isdigit, text))
    
    if not period_id:
        await update.message.reply_text("പീരിയഡ് നമ്പർ കണ്ടെത്താനായില്ല.")
        return

    if period_id in period_data:
        number, result_type = period_data[period_id]
    else:
        number = random.randint(0, 9)
        result_type = "Small" if number <= 4 else "Big"
        period_data[period_id] = (number, result_type)
    
    await update.message.reply_text(f"🎯 Prediction for {period_id}:\nNumber: {number}\nResult: {result_type}")

if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    
    # ഫോട്ടോ ഹാൻഡ്‌ലർ
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Bot is running...")
    application.run_polling()
