import os
import time

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


import requests

from logger import log
from fb_post import FbPost


class FbPostUtil(object):
    """docstring for FbPost"""

    def __init__(self, config):
        super(FbPostUtil, self).__init__()
        self.driver = None
        for key in config:
            setattr(self, key, config[key])

    def wait_until(self, css, wait_time=20):
        driver = self.get_driver()
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
        response = session.post(self.loginUrl, data={
                     "email": self.fbUsername, "pass": self.fbPassword})
        cookies = session.cookies.get_dict()
        return cookies

    def take_screenshot(self):
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.driver.save_screenshot(os.path.join(dir_path,'errors',str(time.time())+".png"))

    def get_driver(self):
        if self.driver is None:
            cookies = self.login()
            chrome_options = webdriver.ChromeOptions()
            prefs = {"profile.default_content_setting_values.notifications": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.set_headless(headless=True)
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(self.indexUrl)
            for key in cookies:
                driver.add_cookie({'name': key, 'value': cookies[key]})
            self.driver = driver
        return self.driver

    def open_page(self,reopen = False):
        if reopen or not self.get_driver().startswith(self.pageUrl):
            self.get_driver().get(self.pageUrl)

    def post_media(self,fb_post):
        self.open_page()
        post_msg = fb_post.post_msg.encode("ascii", "ignore").decode(
                        "ascii") if fb_post.post_msg is not None else ""
        retry_count = 0
        while retry_count < 3:
            try:
                el = self.wait_until("ul[data-testid=collapsed_sprouts] li:first-child input[type=file]",1)
                if(el is None):
                    self.wait_until("div[data-testid=photo-video-button]").click()
                    el = self.wait_until( "div[data-testid=media-attachment-buttons] tr:first-child input[type=file]")
                el.send_keys(fb_post.media_path)
                if fb_post.post_type == FbPost.IMAGE:
                    self.wait_until("div[data-testid=status-attachment-mentions-input]").click()
                    self.wait_until( "div[data-testid=media-attachment-photo] img")
                    self.wait_until( "div[data-testid=status-attachment-mentions-input]").send_keys(post_msg)
                    self.wait_until("button[data-testid=react-composer-post-button]").click()
                elif fb_post.post_type == FbPost.VIDEO:
                    #self.wait_until(driver,"div[id*=placeholder]").send_keys(post_msg)
                    self.wait_until("div[data-testid=video_upload_complete_bar]")
                    self.wait_until("input[data-testid=VIDEO_TITLE_BAR_TEXT_INPUT]").send_keys("Video_"+str(int(time.time())))
                    self.wait_until("a[data-testid=VIDEO_COMPOSER_NEXT_BUTTON]").click()
                    self.wait_until("a[data-testid=VIDEO_COMPOSER_PUBLISH_BUTTON]").click()
                    self.wait_until("div[data-testid=VIDEO_COMPOSER_CONFIRM_DIALOG]")
                break
            except Exception as e:
                log.error(e)
                log.error("Failed ..! Retrying "+ str(retry_count))
                self.take_screenshot()
                self.open_page(reopen=True)
                if EC.alert_is_present():
                    self.driver.switch_to.alert.accept()
                retry_count = retry_count + 1
    def exit(self):
        if self.driver is not None:
            self.driver.quit()

            
