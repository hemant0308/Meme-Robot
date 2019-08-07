import sys
import os

from lxml import html as parser
from lxml import etree

import time
import threading
import html
import json
import random
import math
from datetime import datetime

import requests

from logger import log

from lxml_utils import get_el_attr_by_css
from lxml_utils import get_el_text_by_css
from lxml_utils import get_el_by_css

dir_path = os.path.dirname(os.path.realpath(__file__))
data = {}


class FbRequest(object):
    """docstring for Fb_request"""

    def __init__(self, config):
        super(FbRequest, self).__init__()
        for key in config:
            setattr(self, key, config[key])

    def parse_str(self, raw_str, page_name):
        posts = []
        json_data = json.loads(raw_str)
        html_str = json_data['domops'][0][3]['__html']
        html_str = html.unescape(html_str)
        htmltree = parser.fromstring(html_str)
        posts_el = htmltree.cssselect(".userContentWrapper")
        data_array = json_data['jsmods']['pre_display_requires']
        array_len = len(data_array)
        posts_count = int(array_len/2)

        index = 0
        for post_el in posts_el:
            try:
                post = self.get_post(post_el)
                feedback_obj = data_array[posts_count +
                                          index][3][1]['__bbox']['result']['data']['feedback']
                comment_count = feedback_obj['i18n_comment_count']
                reaction_count = feedback_obj['i18n_reaction_count']
                share_count = feedback_obj['i18n_share_count']
                post.set_feedback(comment_count, reaction_count,
                                  share_count, page_name)
                posts.append(post)
            except Exception as e:
                log.error(pageName)
                log.error(e)
                pass
            index = index + 1
        log.error("parsing posts for "+str(page_name) +
                  " count is : "+str(len(posts)))
        return posts

    def get_post(self, post_el):
        img_src = get_el_attr_by_css(post_el, ".scaledImageFitWidth", "src")
        post_msg = get_el_text_by_css(
            post_el, "div[data-testid='post_message']")
        posted_time = int(get_el_attr_by_css(
            post_el, 'abbr[data-utime]', "data-utime"))
        # Removing 12:30 hours to match with indian time.
        posted_time = posted_time - (12 * 60 * 60 - 30 * 60)
        return FbPost(self.deviation, img_src=img_src, post_msg=post_msg, posted_time=posted_time)

    def get_page_posts(self, page_id, page_name):
        current_time = time.time()
        prev_filtered_posts = []
        is_all_fetched = False
        posts_count = self.postsChunk
        lastJobRunAt = self.lastJobRunAt
        url_formats = self.urlFormats
        retry_count = 0
        while not is_all_fetched and retry_count < len(url_formats):
            url = self.construct_url(
                page_id, posts_count, url_formats[retry_count])
            log.error('fetching from : '+str(url) +
                      ' for the page '+str(page_name))
            response = requests.get(url)
            raw_str = response.content.decode('UTF-8')
            raw_str = raw_str.replace('for (;;);', '')
            all_posts = []
            try:
                all_posts = self.parse_str(raw_str, page_name)
            except Exception as e:
                retry_count = retry_count + 1
                print("Retrying second time for ", page_name)
                log.error(e)
                continue
            filtered_posts = []
            exceeded_count = 0
            for post in all_posts:
                if post.posted_time < lastJobRunAt:
                    exceeded_count = exceeded_count + 1
                if(post.img_src is not None):
                    filtered_posts.append(post)
            if len(filtered_posts) == len(prev_filtered_posts):
                log.error("No more posts")
                break
            prev_filtered_posts = filtered_posts
            if exceeded_count > 1:
                is_all_fetched = True
                log.error("All fetched")
                break
            posts_count = posts_count+self.postsChunk
        if retry_count >= len(url_formats):
            log.error("Unable to fetch posts from "+str(page_name))
        total_posts_array = []
        for post in prev_filtered_posts:
            if post.posted_time >= lastJobRunAt:
                total_posts_array.append(post)
        return total_posts_array

    def get_page_posts_by_pageIds(self, pagesData, total_posts_array=[]):
        for page in pagesData:
            posts = self.get_page_posts(page['pageId'], page['pageName'])
            for post in posts:
                total_posts_array.append(post)

    def construct_url(self, page_id, posts_count, url_format):
        return url_format.replace("{{pageId}}", page_id).replace("{{postsCount}}", str(posts_count))


class FbPost(object):
    """docstring for FbPost"""

    def __init__(self, deviation, **kwargs):
        super(FbPost, self).__init__()
        self.deviation = deviation
        self.img_src = kwargs["img_src"]
        self.posted_time = kwargs["posted_time"] + self.deviation
        self.post_msg = kwargs["post_msg"]
        self.local_path = None

    def set_feedback(self, comment_count, reaction_count, share_count, page_name):
        self.comment_count = self.convert_to_number(comment_count)
        self.share_count = self.convert_to_number(share_count)
        self.reaction_count = self.convert_to_number(reaction_count)
        self.page_name = page_name
        if self.img_src is None:
            self.reach_count = 0
        else:
            self.reach_count = (self.share_count * 2) + \
                (self.reaction_count) + (self.comment_count * 1.2)

    def convert_to_number(self, reach_count_str="0"):
        try:
            reach_count_str = reach_count_str.lower()
            if 'k' in reach_count_str or 'వే' in reach_count_str:
                return int(1000 * float(reach_count_str.replace('k', '').replace('వే', '')))
            elif 'm' in reach_count_str:
                return int(1000000 * float(reach_count_str.replace('m', '')))
            else:
                return int(reach_count_str)
        except Valueerror as e:
            log.error(e)
            return 0

    def __str__(self):
        return ("Page name : "+self.page_name+"\nImage Src : "+str(self.img_src)+"\nPosted Time : "+str(time.strftime('%m/%d/%Y, %H:%M:%S', time.localtime(self.posted_time)))
                + "\nTime stamp : "+str(self.posted_time)+"\nShare Count : "+str(self.share_count)+"\nComment Count : "+str(self.share_count)+"\nReaction Count : "+str(self.reaction_count)+"\nPost Message: "+str(self.post_msg)+"\nReach count :"+str(self.reach_count)+"\n")


def get_top_posts(data):
    fb_request = FbRequest(data)
    def cmp(a,b):
        return a['pageId'] == b['pageId']
    pagesData = remove_duplicates(data['pagesData'],fn=cmp)
    no_of_threads = data['noOfThreads']
    chunks = get_random_chunks(pagesData, no_of_threads)
    posts = []
    threads = []
    for chunk in chunks:
        thread = threading.Thread(
            target=fb_request.get_page_posts_by_pageIds, args=(chunk, posts,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    def cmp(a,b):
        a.img_src == b.img_src    
    log.error("Total posts Count : {}".format(len(posts)))
    posts = remove_duplicates(posts,fn=cmp)
    posts.sort(key=lambda a: a.reach_count, reverse=True)
    log.error("Total posts Count : {}".format(len(posts)))
    sent_count = min(int(len(posts)*.3), 10)
    sent_count = max(sent_count, len(posts)) if sent_count < 3 else sent_count
    top_count = int(sent_count/2)
    random_count = sent_count - top_count
    return posts[:top_count] + random.sample(posts[top_count:], random_count)


def get_random_chunks(pageIds, no_of_threads):
    random.shuffle(pageIds)
    chunk_size = math.ceil(len(pageIds)/no_of_threads)
    remainder = len(pageIds) % no_of_threads
    iterator = 0
    chunks_count = no_of_threads
    while chunks_count > 1:
        yield pageIds[iterator:(iterator+chunk_size)]
        chunks_count = chunks_count - 1
        remainder = remainder - 1
        iterator = iterator + chunk_size
        if remainder == 0:
            chunk_size = chunk_size - 1
    yield pageIds[iterator:]


def remove_duplicates(pagesData,fn=None):
    temp_array = []
    for page in pagesData:
        is_pushed = False
        for _page in temp_array:
            if fn is not None:
                if fn(_page,page):
                    is_pushed = True
                    break
            else:
                if _page == page:
                    is_pushed = True
                    break
        if not is_pushed:
            temp_array.append(page)
    return temp_array
