import os

import json
import time
import datetime


from utils import get_top_posts,post_FbPosts,print_log

dir_path = os.path.dirname(os.path.realpath(__file__))

def main():
    try:
        start_time = time.time()
        with open(os.path.join(dir_path,"data.json")) as f:
            data = json.load(f)
        top_posts = get_top_posts(data)
        for post in top_posts:
            print_log(post)
        post_FbPosts(data,top_posts)
        print_log("Total posts posted : "+str(len(top_posts)))
        print_log("Time taken : "+str(time.time() - start_time))
    except Exception as e:
        print(e)
    print(datetime.datetime.now()," :: Done successfully")

if __name__ == '__main__':
    main()
    pass