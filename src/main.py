import os

import json
import time
import datetime


from request_utils import get_top_posts
from selenium_utils import FbPostUtil
from email_utils import send_mail
from media_utils import MediaUtils
from fb_post import FbPost
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

        media_utils = MediaUtils(data)

        fb_posts = []
        for fb_post in top_posts:
            try:
                if fb_post.post_type == FbPost.VIDEO:
                    fb_post.media_path = media_utils.download_video(fb_post)
                else:
                    fb_post.media_path = media_utils.download_img(fb_post)
                fb_posts.append(fb_post)
            except Exception as e:
                pass

        for post in top_posts:
            log.error(post)

        if(len(top_posts) > 0):
            fb_utils = FbPostUtil(data)
            fb_utils.post_photos(fb_posts)
        if(data['sendMail']):
            send_mail(top_posts)
            log.error("Mail sent")

        log.error("Total posts posted : "+str(len(top_posts)))
        log.error("Time taken : "+str(time.time() - start_time))

        data["lastJobRunAt"] = int(time.time())
        with open('data/config.json', 'w') as f:
             json.dump(data, f, indent=4, sort_keys=True)
        
        media_utils.clean_media()
        print(str(datetime.datetime.now())+" :: success")

    except Exception as e:
        raise e
        print(e)
        print(str(datetime.datetime.now())+" :: Failed")
    log.error(str(datetime.datetime.now())+" :: Done successfully")

if __name__ == '__main__':
    main()