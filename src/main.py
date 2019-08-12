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

        with open(os.path.join(data_dir,"data/fbPosts.json")) as f:
            previous_posts = json.load(f)

        top_posts = get_top_posts(data)

        media_utils = MediaUtils(data)
        fb_post_utils = FbPostUtil(data)
        for fb_post in top_posts:
            log.error(fb_post)
            is_posted = False
            for prev_post in previous_posts:
                if prev_post['post_url'] == fb_post.post_url:
                    is_posted = True
                    break
            if not is_posted:
                try:
                    if fb_post.post_type == FbPost.VIDEO:
                        fb_post.media_path = media_utils.download_video(fb_post)
                    else:
                        fb_post.media_path = media_utils.download_img(fb_post)
                    fb_post_utils.post_media(fb_post)
                    fb_post.mark_as_done()
                    previous_posts.append(fb_post.get_dict())
                    log.error("Success")
                except Exception as e:
                    raise e
                    log.error("Failure")
            else:
                log.error("This post posted already")
        fb_post_utils.exit()
        if(data['sendMail']):
            send_mail(top_posts)
            log.error("Mail sent")

        log.error("Total posts posted : "+str(len(top_posts)))
        log.error("Time taken : "+str(time.time() - start_time))

        data["lastJobRunAt"] = int(time.time())
        with open('data/config.json', 'w') as f:
             json.dump(data, f, indent=4, sort_keys=True)

        previous_posts_bkp = []
        for prev_post in previous_posts:
            if prev_post['completed_time'] > time.time() - data["maxPostsToKeep"]:
                previous_posts_bkp.append(prev_post)

        with open(os.path.join(data_dir,"data/fbPosts.json"), 'w') as f:
             json.dump(previous_posts_bkp, f, indent=4, sort_keys=True)
        
        media_utils.clean_media()
        print(str(datetime.datetime.now())+" :: success")

    except Exception as e:
        raise e
        print(e)
        print(str(datetime.datetime.now())+" :: Failed")
    log.error(str(datetime.datetime.now())+" :: Done successfully")

if __name__ == '__main__':
    main()