import os
import time

import requests
from PIL import Image

def download_img(img_src):
    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    img_name = os.path.join(dir_path,"images",str(time.time())+".png")
    img = Image.open(requests.get(img_src, stream=True).raw)
    img.save(img_name)
    return img_name

def clean_images():
    images = os.listdir("images/")
    if(len(images) > 100):
        images.sort()
        for i in range(len(images) - 5):
            os.unlink(images[i])
