from appium import webdriver
import time
import operator
import re
import datetime
import json
from selenium.webdriver.support.ui import WebDriverWait
import shutil
import os
import pymongo
 
class Action():
    def __init__(self):
        self.desired_caps = {
            "platformName": "Android",
            "deviceName": "OnePlus3",
            "appPackage": "com.ss.android.article.news",
            "appActivity": "com.ss.android.article.news.activity.SplashActivity",
            "noReset": "True",
            "unicodeKeyboard": "True",
            "resetKeyboard": "True"
        }
        self.server = 'http://localhost:4723/wd/hub'
        self.driver = webdriver.Remote(self.server, self.desired_caps)
        self.items = list()
        # mongo
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['toutiao-db']
        self.user_video_stop = self.db['user.video.stop']
    def comments(self):
        time.sleep(10)
    def downSwipe_m(self):
        self.driver.swipe(430, 1500, 430, 800)
    def downSwipe_s(self):
        self.driver.swipe(430, 1500, 430, 1400)
    def find_elements_by_xpath(self, xpath):
        while True:
            try:
                l = self.driver.find_elements_by_xpath(xpath)
                if len(l) == 0:
                    time.sleep(1)
                    continue
                else:
                    return l[0]
            except :
                time.sleep(1)
                continue
    def clear(self):
        self.items.clear()
    def me(self):
        self.find_elements_by_xpath('//android.widget.TextView[@text="我的"]').click()
    def liker(self, user, isFull):
        # tap likers
        self.find_elements_by_xpath('//android.widget.TextView[@text="关注"]').click()
        # tap user
        self.clear()
        self.tapAuser(user, isFull)
        time.sleep(1)
        self.driver.back()
    def tapAuser(self, userName, isFull):
        self.userName = userName
        self.user_video_stop.update_one({'source': userName}, { '$set': { 'source': userName, 'complete_count': 0}}, True)
        user_path = "//android.widget.TextView[@text=\"{}\"]".format(userName)
        while True:
            users = self.driver.find_elements_by_xpath(user_path)
            if len(users) == 0:
                self.downSwipe_m()
                time.sleep(1)
            else:
                users[0].click()
                break
        # tap video
        while True:
            elm = self.find_elements_by_xpath('//android.widget.TextView[@text="视频"]')
            elm.click()
            if elm.is_selected():
                break
            time.sleep(1)
        # collectting
        self.collectMedia(userName, isFull)

    def collectMedia(self, name, isFull):
        is_loop = True
        while is_loop:
            medias = self.driver.find_elements_by_id('com.ss.android.article.news:id/b62')
            for media in medias:
                doc = self.user_video_stop.find_one({"source": name})
                if doc["complete_count"] >= 5 and not isFull:
                    is_loop = False
                    break
                else:
                    media.click()
                    time.sleep(0.5)
            try:
                self.downSwipe_m()
                noMore = self.driver.find_elements_by_id('com.ss.android.article.news:id/z0')
                if len(noMore) != 0:
                    if noMore[0].get_attribute('text') == "暂无更多内容":
                        print(noMore[0].get_attribute('text'))
                        break
            except: 
                continue

    


if __name__ == '__main__':
    action = Action()
    action.me()
    action.liker("一点观世界", False)
    action.liker("乐播大剧", False)