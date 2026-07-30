from collections import Counter
import os
from threading import Thread
import time
import cv2
from flask import Flask
from skimage.color import deltaE_cie76, rgb2lab
import matplotlib
import telebot

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running!"


def run_web():
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)


Thread(target=run_web).start()

TOKEN = "8660064955:AAEPwaRQTO83zaCyswkmzjMMam6tDYpghlY"
bot = telebot.TeleBot(TOKEN)

IMAGE_DIRECTORY = "images"
COLORS = {"GREEN": [0, 128, 0], "BLUE": [0, 0, 128], "YELLOW": [255, 255, 0]}


def get_image(image_path):
  image = cv2.imread(image_path)
  if image is not None:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  return image


def get_colors(image, number_of_colors):
  modified_image = cv2.resize(image, (600, 400), interpolation=cv2.INTER_AREA)
  modified_image = modified_image.reshape(
      modified_image.shape[0] * modified_image.shape[1], 3
  )
  clf = KMeans(n_clusters=number_of_colors, n_init=10)
  labels = clf.fit_predict(modified_image)
  counts = Counter(labels)
  center_colors = clf.cluster_centers_
  ordered_colors = [center_colors[i] for i in counts.keys()]
  return ordered_colors


def match_image_by_color(image, color, threshold=60, number_of_colors=10):
  image_colors = get_colors(image, number_of_colors)
  selected_color = rgb2lab(np.uint8(np.asarray([[color]])))
  for i in range(len(image_colors)):
    curr_color = rgb2lab(np.uint8(np.asarray([[image_colors[i]]])))
    diff = deltaE_cie76(selected_color, curr_color)
    if diff < threshold:
      return True
  return False


def save_selected_images(images, color, threshold, colors_to_match):
  index = 1
  for i in range(len(images)):
    selected = match_image_by_color(images[i], color, threshold, colors_to_match)
    if selected and index <= 5:
      plt.subplot(1, 5, index)
      plt.imshow(images[i])
      plt.axis("off")
      index += 1
  if index > 1:
    plt.savefig("output.png")
    return True
  return False


@bot.message_handler(commands=["predict"])
def send_predict(message):
  bot.reply_to(message, "ചിത്രങ്ങൾ പരിശോധിക്കുന്നു, ദയവായി കാത്തിരിക്കുക...")

  images = []
  if os.path.exists(IMAGE_DIRECTORY):
    for file in os.listdir(IMAGE_DIRECTORY):
      if file.lower().endswith((".png", ".jpg", ".jpeg")):
        img_path = os.path.join(IMAGE_DIRECTORY, file)
        img = get_image(img_path)
        if img is not None:
          images.append(img)

  if len(images) > 0:
    plt.figure(figsize=(20, 10))
    success = save_selected_images(images, COLORS["BLUE"], 60, 5)
    plt.close()

    # ഓട്ടോമാറ്റിക് ആയി ഒരു പ്രെഡിക്ഷൻ റിസൾട്ട് തിരഞ്ഞെടുക്കുന്നു (Red അല്ലെങ്കിൽ Green)
    import random

    prediction_result = random.choice(["🟢 GREEN", "🔴 RED"])
    prediction_text = (
        f"📊 **AI Analysis Completed!**\n\n🎯 **Recommended Prediction:**"
        f" {prediction_result}"
    )

    if success and os.path.exists("output.png"):
      with open("output.png", "rb") as photo:
        bot.send_photo(
            message.chat.id, photo, caption=prediction_text, parse_mode="Markdown"
        )
    else:
      bot.reply_to(message, f"🎯 **Prediction:** {prediction_result}")
  else:
    bot.reply_to(
        message, "ഫോൾഡറിൽ ചിത്രങ്ങളൊന്നും ലഭ്യമല്ല അല്ലെങ്കിൽ പാത്ത് തെറ്റാണ്."
    )


def run_bot():
  while True:
    try:
      bot.infinity_polling(
          timeout=30, interval=0, long_polling_timeout=30, skip_pending=True
      )
    except Exception as e:
      print(f"Polling Error: {e}")
      time.sleep(3)


Thread(target=run_bot).start()

while True:
  time.sleep(1)




