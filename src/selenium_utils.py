import os
import time

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import requests

from logger import log
from media_utils import download_img


class FbPostUtil(object):
    """docstring for FbPost"""

    def __init__(self, config):
        super(FbPostUtil, self).__init__()
        for key in config:
            setattr(self, key, config[key])

    def wait_until(self, driver, css, wait_time=20):
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

    def login(self):
        session = requests.session()
        session.get(self.indexUrl)
        session.post(self.loginUrl, data={
                     "email": self.fbUsername, "pass": self.fbPassword})
        cookies = session.cookies.get_dict()
        return cookies

    def post_photos(self, fb_posts):
        cookies = self.login()

        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.set_headless(headless=True)
        driver = webdriver.Chrome(chrome_options=chrome_options)

        driver.get(self.indexUrl)
        for key in cookies:
            driver.add_cookie({'name': key, 'value': cookies[key]})

        driver.get(self.pageUrl)
        for fb_post in fb_posts:
            retry_count = 0
            while retry_count < 3:
                try:
                    el = self.wait_until(
                        driver, "ul[data-testid=collapsed_sprouts] li:first-child input[type=file]", 1)
                    css = 'ul[data-testid=collapsed_sprouts] li:first-child input[type=file]'
                    if(el is None):
                        self.wait_until(
                            driver, "div[data-testid=photo-video-button]").click()
                        el = self.wait_until(
                            driver, "div[data-testid=media-attachment-buttons] tr:first-child input[type=file]")
                        css = 'div[data-testid=media-attachment-buttons] tr:first-child input[type=file]'
                    el.send_keys(fb_post.local_path)
                    self.wait_until(
                        driver, "div[data-testid=status-attachment-mentions-input]").click()
                    self.wait_until(
                        driver, "div[data-testid=media-attachment-photo] img")
                    msg = fb_post.post_msg.encode("ascii", "ignore").decode(
                        "ascii") if fb_post.post_msg is not None else ""
                    self.wait_until(
                        driver, "div[data-testid=status-attachment-mentions-input]").send_keys(msg)
                    driver.find_element_by_css_selector(
                         "button[data-testid=react-composer-post-button]").click()
                    time.sleep(5)
                    break
                except Exception as e:
                    log.error(e)
                    log.error("Failed ..! Retrying ", str(retry_count))
                    driver.get(self.pageUrl)
                    retry_count = retry_count + 1


def post_photos(config, fb_posts):
    fb_post_util = FbPostUtil(config)
    fb_post_util.post_photos(fb_posts)
