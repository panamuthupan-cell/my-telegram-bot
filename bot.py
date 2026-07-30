from collections import Counter
import os
from threading import Thread
import time
import cv2
from flask import Flask
from skimage.color import deltaE_cie76, rgb2lab
import matplotlib
import telebot

matplotlib.use("Agg")  # സർവറിൽ പ്ലോട്ട് വർക്ക് ചെയ്യാൻ
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

# 1. Render-നായി ചെറിയ ഒരു ഡമ്മി വെബ് സർവർ (പോർട്ട് ബൈൻഡ് ചെയ്യാൻ)
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running!"


def run_web():
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)


# വെബ് സർവർ ബാക്ക്ഗ്രൗണ്ടിൽ സ്റ്റാർട്ട് ചെയ്യുന്നു
Thread(target=run_web).start()

# 2. ടെലിഗ്രാം ബോട്ട് സെറ്റപ്പ്
TOKEN = "8660064955:AAEPwaRQTO83zaCyswkmzjMMam6tDYpghlY"
bot = telebot.TeleBot(TOKEN)

IMAGE_DIRECTORY = "."  # ഗിത്ഹബ് മെയിൻ ഫോൾഡറിൽ നിന്ന് ചിത്രങ്ങൾ എടുക്കാൻ
COLORS = {"GREEN": [0, 128, 0], "BLUE": [0, 0, 128], "YELLOW": [255, 255, 0]}


# RGB മുതൽ HEX വരെയുള്ള മാറ്റം
def RGB2HEX(color):
  return "#{:02x}{:02x}{:02x}".format(
      int(color[0]), int(color[1]), int(color[2])
  )


def get_image(image_path):
  image = cv2.imread(image_path)
  if image is not None:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  return image


# ചിത്രങ്ങളിൽ നിന്ന് നിറങ്ങൾ വേർതിരിക്കുന്നു
def get_colors(image, number_of_colors, show_char=True):
  modified_image = cv2.resize(image, (600, 400), interpolation=cv2.INTER_AREA)
  modified_image = modified_image.reshape(
      modified_image.shape[0] * modified_image.shape[1], 3
  )

  clf = KMeans(n_clusters=number_of_colors, n_init=10)
  labels = clf.fit_predict(modified_image)

  counts = Counter(labels)
  center_colors = clf.cluster_centers_

  ordered_colors = [center_colors[i] for i in counts.keys()]
  rgb_colors = [ordered_colors[i] for i in counts.keys()]

  return rgb_colors


# നിറം അനുസരിച്ച് ചിത്രം മാച്ച് ചെയ്യുന്നു
def match_image_by_color(image, color, threshold=60, number_of_colors=10):
  image_colors = get_colors(image, number_of_colors, False)
  selected_color = rgb2lab(np.uint8(np.asarray([[color]])))

  select_image = False
  for i in range(len(image_colors)):
    curr_color = rgb2lab(np.uint8(np.asarray([[image_colors[i]]])))
    diff = deltaE_cie76(selected_color, curr_color)
    if diff < threshold:
      select_image = True
      break

  return select_image


# തിരഞ്ഞെടുത്ത ചിത്രങ്ങൾ സേവ് ചെയ്യുന്നു
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


# 3. ടെലിഗ്രാം കമാൻഡ് ഹാൻഡ്‌ലർ
@bot.message_handler(commands=["predict"])
def send_predict(message):
  bot.reply_to(message, "ചിത്രങ്ങൾ പരിശോധിക്കുന്നു, ദയവായി കാത്തിരിക്കുക...")

  images = []
  if os.path.exists(IMAGE_DIRECTORY):
    for file in os.listdir(IMAGE_DIRECTORY):
      # ചിത്രങ്ങൾ മാത്രം എടുക്കാനായി എക്സ്റ്റൻഷൻ പരിശോധിക്കുന്നു
      if file.lower().endswith((".png", ".jpg", ".jpeg")):
        img_path = os.path.join(IMAGE_DIRECTORY, file)
        img = get_image(img_path)
        if img is not None:
          images.append(img)

  if len(images) > 0:
    plt.figure(figsize=(20, 10))
    success = save_selected_images(images, COLORS["BLUE"], 60, 5)
    plt.close()  # മെമ്മറി ക്ലിയർ ചെയ്യാൻ

    if success and os.path.exists("output.png"):
      with open("output.png", "rb") as photo:
        bot.send_photo(message.chat.id, photo, caption="മാച്ച് ചെയ്ത ചിത്രങ്ങൾ!")
    else:
      bot.reply_to(
          message, "മാച്ച് ചെയ്യുന്ന കളറിലുള്ള ചിത്രങ്ങളൊന്നും കണ്ടെത്തിയില്ല."
      )
  else:
    bot.reply_to(
        message, "ഫോൾഡറിൽ ചിത്രങ്ങളൊന്നും ലഭ്യമല്ല അല്ലെങ്കിൽ പാത്ത് തെറ്റാണ്."
    )


# 4. ബോട്ട് ബാക്ക്ഗ്രൗണ്ടിൽ റൺ ചെയ്യാൻ ത്രെഡ് ഉപയോഗിക്കുന്നു
def run_bot():
  while True:
    try:
      bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
      print(f"Error: {e}")
      time.sleep(5)


Thread(target=run_bot).start()

# ആപ്പ് ലൈവായി നിലനിർത്താൻ
while True:
  time.sleep(1)
