import os
import time

from lxml import html as parser
from lxml_utils import get_attr_by_css
from logger import log

import requests
from PIL import Image

class MediaUtils(object):
    IMAGE = 'image'
    VIDEO = 'video'
    """docstring for MediaUtils"""
    def __init__(self, config):
        super(MediaUtils, self).__init__()
        for key in config:
            setattr(self,key,config[key])

    def download_img(self,fb_post):
        img = Image.open(requests.get(fb_post.img_src, stream=True).raw)
        img_name = self.get_filename(self.IMAGE)
        img.save(img_name)
        return img_name

    def clean_media(self):
        self.clean_images()
        self.clean_videos()

    def get_filename(self,file_type):
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        if file_type == self.IMAGE:
            return os.path.join(dir_path,"images",str(time.time())+".png")
        else:
            return os.path.join(dir_path,"videos",str(time.time())+".mp4")

    def download_video(self,fb_post):
        log.error(fb_post)
        video_url = self.build_url(fb_post.page_name,fb_post.video_id)
        response = requests.get(video_url)
        html_text = response.content.decode("utf-8")
        el = parser.fromstring(html_text)
        download_link = get_attr_by_css(el,'ul.download-options li:nth-child(2) a','href')
        file_name = self.get_filename(self.VIDEO)
        self.download_file(download_link,file_name)
        return file_name

    def download_file(self,url,file_name):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk: 
                        f.write(chunk)
    def build_url(self,pageName,video_id):
        return self.videoUrl.replace("{{pageName}}",pageName).replace("{{videoId}}",video_id)

    def clean_images(self):
        images = os.listdir("images/")
        if(len(images) > self.maxImagesToKeep):
            images.sort()
            for i in range(len(images) - self.maxImagesToKeep):
                os.unlink(images[i])

    def clean_videos(self):
        images = os.listdir("videos/")
        if(len(images) > self.maxVideosToKeep):
            images.sort()
            for i in range(len(images) - self.maxVideosToKeep):
                os.unlink(images[i])