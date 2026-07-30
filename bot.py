from collections import Counter
import os
from threading import Thread
import cv2
from flask import Flask
from skimage.color import deltaE_cie76, rgb2lab
import matplotlib

matplotlib.use("Agg")  # GUI ഇല്ലാത്ത സർവറുകളിൽ പ്ലോട്ട് വർക്ക് ചെയ്യാൻ
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

# 1. Render-നായി ചെറിയ ഒരു ഡമ്മി വെബ് സർവർ (പോർട്ട് എയ്ഡ് ചെയ്യാൻ)
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running!"


def run_web():
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)


# ബാക്ക്ഗ്രൗണ്ടിൽ വെബ് സർവർ സ്റ്റാർട്ട് ചെയ്യുന്നു
Thread(target=run_web).start()


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


# 2. Render-ൽ ഉള്ള ഫോൾഡർ പാത്ത് (ഇല്ലെങ്കിൽ നിലവിലുള്ള ഫോൾഡർ നൽകുക)
IMAGE_DIRECTORY = "./images"  # അല്ലെങ്കിൽ നിങ്ങളുടെ പ്രൊജക്റ്റിലെ ഇമേജ് ഫോൾഡർ പാത്ത്
COLORS = {"GREEN": [0, 128, 0], "BLUE": [0, 0, 128], "YELLOW": [255, 255, 0]}
images = []

# ഡയറക്ടറിയിൽ നിന്ന് ചിത്രങ്ങൾ എടുക്കുന്നു
if os.path.exists(IMAGE_DIRECTORY):
  for file in os.listdir(IMAGE_DIRECTORY):
    if not file.startswith("."):
      img_path = os.path.join(IMAGE_DIRECTORY, file)
      img = get_image(img_path)
      if img is not None:
        images.append(img)


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


# തിരഞ്ഞെടുത്ത ചിത്രങ്ങൾ സേവ് ചെയ്യുന്നു (സെർവറിൽ plt.show() വർക്ക് ആകില്ല)
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
    plt.savefig("output.png")  # ചിത്രങ്ങൾ ഫയലായി സേവ് ചെയ്യുന്നു
    print("Matched images saved to output.png")


# പ്രോസസ്സിംഗ്
if len(images) > 0:
  plt.figure(figsize=(20, 10))
  save_selected_images(images, COLORS["BLUE"], 60, 5)
else:
  print("ചിത്രങ്ങളൊന്നും കണ്ടെത്തിയില്ല.")

# ആപ്പ് പെട്ടെന്ന് ക്ലോസ് ആയി പോകാതിരിക്കാൻ ലൂപ്പ് നിലനിർത്തുന്നു
import time

while True:
  time.sleep(1)
