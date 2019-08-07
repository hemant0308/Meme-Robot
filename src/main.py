import os

import json
import time
import datetime


from request_utils import get_top_posts
from selenium_utils import post_photos
from email_utils import send_mail
from media_utils import download_img,clean_images
from logger import log

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path.split()
    try:
        start_time = time.time()

        data_dir = os.path.dirname(dir_path)
        with open(os.path.join(data_dir,"data/config.json")) as f:
            data = json.load(f)

        top_posts = get_top_posts(data)

        for fb_post in top_posts:
            fb_post.local_path = download_img(fb_post.img_src)

        for post in top_posts:
            log.error(post)

        if(len(top_posts) > 0):
            post_photos(data,top_posts)

        send_mail(top_posts)

        log.error("Total posts posted : "+str(len(top_posts)))
        log.error("Time taken : "+str(time.time() - start_time))

        data["lastJobRunAt"] = int(time.time())
        with open('data/config.json', 'w') as f:
             json.dump(data, f, indent=4, sort_keys=True)
        
        clean_images()

    except Exception as e:
        raise e
        print(e)
    print(datetime.datetime.now()," :: Done successfully")

if __name__ == '__main__':
    main()