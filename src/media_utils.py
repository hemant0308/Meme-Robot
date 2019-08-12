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
        file_name = self.get_filename(self.VIDEO)
        retry_count = 0
        while True:
            try:
                video_url = self.build_url(fb_post.page_name,fb_post.video_id)
                response = requests.get(video_url)
                html_text = response.content.decode("utf-8")
                el = parser.fromstring(html_text)
                download_link = get_attr_by_css(el,'ul.download-options li:nth-child(2) a','href')
                self.download_file(download_link,file_name)
                break
            except Exception as e:
                if retry_count > 3:
                    raise Exception("Max retries exceeded to download video "+str(fb_post.video_id))
                retry_count = retry_count + 1
                log.error("Error in downloading video. Retrying ("+str(retry_count)+")")

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
                os.unlink(os.path.join('images',images[i]))

    def clean_videos(self):
        videos = os.listdir("videos/")
        if(len(videos) > self.maxVideosToKeep):
            videos.sort()
            for i in range(len(videos) - self.maxVideosToKeep):
                os.unlink(os.path.join('videos',videos[i]))

    def clean_screeshots(self):
        videos = os.listdir("errors/")
        if(len(videos) > self.maxVideosToKeep):
            videos.sort()
            for i in range(len(videos) - self.maxImagesToKeep):
                os.unlink(os.path.join('errors',videos[i]))