import os
from collections import Counter
import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from skimage.color import rgb2lab
from skimage.color import deltaE_cie76

# RGB മുതൽ HEX വരെയുള്ള മാറ്റം
def RGB2HEX(color): 
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2])) 
 
def get_image(image_path): 
    image = cv2.imread(image_path) 
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 
    return image 
 
IMAGE_DIRECTORY = 'C:/Users/Dell/Desktop/CPS 02' 
COLORS = { 
    'GREEN': [0, 128, 0], 
    'BLUE': [0, 0, 128], 
    'YELLOW': [255, 255, 0] 
} 
images = [] 

# ഡയറക്ടറിയിൽ നിന്ന് ചിത്രങ്ങൾ എടുക്കുന്നു 
# (ശ്രദ്ധിക്കുക: ഈ ഫോൾഡർ നിങ്ങളുടെ കമ്പ്യൂട്ടറിൽ ഉണ്ടെന്ന് ഉറപ്പുവരുത്തുക)
if os.path.exists(IMAGE_DIRECTORY):
    for file in os.listdir(IMAGE_DIRECTORY): 
        if not file.startswith('.'): 
            img_path = os.path.join(IMAGE_DIRECTORY, file)
            img = get_image(img_path)
            if img is not None:
                images.append(img)

# ചിത്രങ്ങളിൽ നിന്ന് നിറങ്ങൾ വേർതിരിക്കുന്നു  
def get_colors(image, number_of_colors, show_char = True): 
    modified_image = cv2.resize(image, (600, 400), interpolation = cv2.INTER_AREA) 
    modified_image = modified_image.reshape(modified_image.shape[0] * modified_image.shape[1], 3) 
 
    clf = KMeans(n_clusters = number_of_colors, n_init=10) 
    labels = clf.fit_predict(modified_image) 
 
    counts = Counter(labels) 
    center_colors = clf.cluster_centers_ 
    
    ordered_colors = [center_colors[i] for i in counts.keys()] 
    hex_colors = [RGB2HEX(ordered_colors[i]) for i in counts.keys()] 
    rgb_colors = [ordered_colors[i] for i in counts.keys()] 
    
    return rgb_colors

# നിറം അനുസരിച്ച് ചിത്രം മാച്ച് ചെയ്യുന്നു 
def match_image_by_color(image, color, threshold = 60, number_of_colors = 10):  
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

# തിരഞ്ഞെടുത്ത ചിത്രങ്ങൾ കാണിക്കുന്നു 
def show_selected_images(images, color, threshold, colors_to_match): 
    index = 1 
    for i in range(len(images)): 
        selected = match_image_by_color(images[i], color, threshold, colors_to_match) 
        if selected: 
            plt.subplot(1, 5, index) 
            plt.imshow(images[i]) 
            plt.axis('off')
            index += 1 

# ഫലം പ്രിന്റ് ചെയ്യുന്നു / പ്ലോട്ട് ചെയ്യുന്നു  
if len(images) > 0:
    plt.figure(figsize = (20, 10)) 
    show_selected_images(images, COLORS['BLUE'], 60, 5)
    plt.show()
else:
    print("ചിത്രങ്ങളൊന്നും gefunden ചെയ്തില്ല അല്ലെങ്കിൽ ഡയറക്ടറി തെറ്റാണ്.")
