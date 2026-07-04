import telebot
import hashlib
import time
from datetime import datetime

API_TOKEN = "8849236484:AAHBUTvNCUGGv69_CxvCRzPeNXKXQXXe8RA"
bot = telebot.TeleBot(API_TOKEN)

def get_live_period():
    now = datetime.now()
    period = now.strftime("%Y%m%d1000") + str(int(time.time() // 60))
    return period

@bot.message_handler(func=lambda message: True)
def auto_predict(message):
    period_text = get_live_period()
    hash_object = hashlib.md5(period_text.encode())
    hash_int = int(hash_object.hexdigest(), 16)
    predicted_number = hash_int % 10

    if predicted_number == 0:
        result_color = "RED & VIOLET"
    elif predicted_number == 5:
        result_color = "GREEN & VIOLET"
    elif predicted_number in [1, 3, 7, 9]:
        result_color = "GREEN"
    else:
        result_color = "RED"

    response_text = (
        f"AUTO PREDICTION\n"
        f"Period: {period_text}\n"
        f"Result: {result_color}\n"
        f"Number: {predicted_number}\n"
    )
    bot.reply_to(message, response_text)

bot.polling(none_stop=True)
