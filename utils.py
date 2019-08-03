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
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image

import smtplib,ssl

dir_path = os.path.dirname(os.path.realpath(__file__))
data = {}
def print_log(*args):
    f = open(os.path.join(dir_path,"logs/meme-robot.log"),"a+")
    msg = ''
    for i in args:
        msg = msg + str(i)
    msg = datetime.now().strftime("%m-%d-%Y, %H:%M:%S :: ")+str(msg) +"\n"
    f.write(msg)
    f.close()

def parse_str(raw_str, page_name):
    posts = []
    try:
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
                post = get_post(post_el)
                feedback_obj = data_array[posts_count +
                                          index][3][1]['__bbox']['result']['data']['feedback']
                comment_count = feedback_obj['i18n_comment_count']
                reaction_count = feedback_obj['i18n_reaction_count']
                share_count = feedback_obj['i18n_share_count']
                post.set_feedback(comment_count, reaction_count,
                                  share_count, page_name)
                posts.append(post)
            except Exception as e:
                print_log(pageName)
                print_log(e)
                pass
            index = index + 1
    except Exception as e:
        print_log(page_name)
        print_log(e)
    return posts


def get_el_text_by_css(el, css):
    el = get_el_by_css(el, css)
    return el.text_content() if el is not None else ""


def get_el_by_css(el, css):
    if el != None:
        elems = el.cssselect(css)
        if(elems != None and len(elems) > 0):
            return elems[0]


def get_el_attr_by_css(el, css, attribute):
    el = get_el_by_css(el, css)
    return el.get(attribute) if el is not None else None


def get_post(post_el):
    img_src = get_el_attr_by_css(post_el, ".scaledImageFitWidth", "src")
    post_msg = get_el_text_by_css(post_el, "div[data-testid='post_message']")
    posted_time = int(get_el_attr_by_css(
        post_el, 'abbr[data-utime]', "data-utime"))
    # Removing 12:30 hours to match with indian time.
    posted_time = posted_time - (12 * 60 * 60 - 30 * 60)
    return FbPost(img_src=img_src, post_msg=post_msg, posted_time=posted_time)


def get_page_posts(page_id, page_name):
    current_time = time.time()
    prev_filtered_posts = []
    is_all_fetched = False
    posts_count = data['postsChunk']
    while not is_all_fetched:
        url = construct_url(page_id, posts_count)
        response = requests.get(url)
        raw_str = response.content.decode('UTF-8')
        raw_str = raw_str.replace('for (;;);', '')
        all_posts = parse_str(raw_str, page_name)
        filtered_posts = []
        exceeded_count = 0
        for post in all_posts:
            if post.posted_time < current_time - (data['timeDuration']):
                exceeded_count = exceeded_count + 1
            if(post.img_src is not None):
                filtered_posts.append(post)
        if len(filtered_posts) == len(prev_filtered_posts):
            print_log("No more posts")
            break
        prev_filtered_posts = filtered_posts
        if exceeded_count > 1:
            is_all_fetched = True
            print_log("All fetched")
            break
        posts_count = posts_count+data['postsChunk']
    total_posts_array = []
    for post in prev_filtered_posts:
        if post.posted_time >= current_time - (data['timeDuration']):
            total_posts_array.append(post)
    return total_posts_array


class FbPost(object):
    """docstring for FbPost"""

    def __init__(self, **kwargs):
        super(FbPost, self).__init__()
        self.img_src = kwargs["img_src"]
        self.posted_time = kwargs["posted_time"] + data["deviation"]
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
        except ValueError as e:
            print_log(e)
            return 0

    def __str__(self):
        return ("Image Src : "+str(self.img_src)+"\nPosted Time : "+str(time.strftime('%m/%d/%Y, %H:%M:%S', time.localtime(self.posted_time)))
                + "\nTime stamp : "+str(self.posted_time)+"\nShare Count : "+str(self.share_count)+"\nComment Count : "+str(self.share_count)+"\nReaction Count : "+str(self.reaction_count)+"\nPost Message: "+str(self.post_msg)+"\nReach count :"+str(self.reach_count)+"\n")


def get_page_posts_by_pageIds(pagesData,total_posts_array=[]):
    for page in pagesData:
        posts = get_page_posts(page['pageId'], page['pageName'])
        for post in posts:
            total_posts_array.append(post)

def get_top_posts(_data):
    global data
    data = _data
    pagesData = data['pagesData']
    chunks = get_random_chunks(pagesData)
    posts = []
    threads = []
    for chunk in chunks:
        thread = threading.Thread(target=get_page_posts_by_pageIds, args=(chunk,posts,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    posts.sort(key=lambda a: a.reach_count, reverse=True)
    print_log("Total posts Count : {}".format(len(posts)))
    sent_count = min(int(len(posts)*.3),10)
    sent_count = max(sent_count,len(posts)) if sent_count < 3 else sent_count
    top_count = int(sent_count/2)
    random_count = sent_count - top_count
    return posts[:top_count] + random.sample(posts[top_count:],random_count)

def construct_url(page_id, posts_count):
    url = data["urlFormat"]
    return url.replace("{{pageId}}", page_id).replace("{{postsCount}}", str(posts_count))


def get_random_chunks(pageIds):
    no_of_threads = data["noOfThreads"]
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

def send_mail(posts):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "hemant0328@gmail.com"
    receiver_email = "hemant0328@gmail.com"
    password = "vnulmsovcfajklyr"
    message = """
    Subject : Last half an our top posts\n"""
    for post in posts:
        message = message + str(post).encode("ascii","ignore").decode("ascii")
    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_server, port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)

def wait_until(driver, css, wait_time=20):
    sleep_time = 1
    while True:
        try:
            el = driver.find_element_by_css_selector(css)
            return el
        except selenium.common.exceptions.NoSuchElementException:
            time.sleep(1)
            sleep_time = sleep_time+1
        if sleep_time > wait_time:
            return None


def login():
    global data
    session = requests.session()
    session.get(data['indexUrl'])
    session.post(data['loginUrl'], data={
                 "email": data['username'], "pass": data['password']})
    cookies = session.cookies.get_dict()
    return cookies


def post_photo(fb_posts, cookies):
    global data
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.set_headless(headless=True)
    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get(data["indexUrl"])
    for key in cookies:
        driver.add_cookie({'name': key, 'value': cookies[key]})

    driver.get(data['pageUrl'])
    for fb_post in fb_posts:
        retry_count = 0
        while retry_count < 3:
            try:
                el = wait_until(
                    driver, "ul[data-testid=collapsed_sprouts] li:first-child input[type=file]", 1)
                css = 'ul[data-testid=collapsed_sprouts] li:first-child input[type=file]'
                if(el is None):
                    wait_until(driver, "div[data-testid=photo-video-button]").click()
                    el = wait_until(
                        driver, "div[data-testid=media-attachment-buttons] tr:first-child input[type=file]")
                    css = 'div[data-testid=media-attachment-buttons] tr:first-child input[type=file]'
                el.send_keys(fb_post.local_path)
                wait_until(
                    driver, "div[data-testid=status-attachment-mentions-input]").click()
                wait_until(driver, "div[data-testid=media-attachment-photo] img")
                msg = fb_post.post_msg.encode("ascii","ignore").decode("ascii") if fb_post.post_msg is not None else ""
                wait_until(
                    driver, "div[data-testid=status-attachment-mentions-input]").send_keys(msg)
                driver.find_element_by_css_selector(
                    "button[data-testid=react-composer-post-button]").click()
                time.sleep(5)
                break
            except Exception as e:
                print_log("Failed ..! Retrying ",retry_count)
                driver.get(data['pageUrl'])
                retry_count = retry_count + 1


def post_FbPosts(_data, fb_posts):
    global data
    data = _data
    index = 1
    for fb_post in fb_posts:
        img_name = os.path.join(dir_path,"images","post_"+str(index)+".png")
        url = fb_post.img_src
        img = Image.open(requests.get(url, stream=True).raw)
        img.save(img_name)
        fb_post.local_path = img_name
        index = index + 1
    cookies = login()
    post_photo(fb_posts, cookies)
    send_mail(fb_posts)
    print_log("******************\n\n")