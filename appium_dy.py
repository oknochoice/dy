from appium import webdriver
from time import sleep
import operator
import re
 
class Action():
    def __init__(self):
        self.desired_caps = {
            "platformName": "Android",
            "deviceName": "ZTEBladeV9",
            "appPackage": "com.ss.android.ugc.aweme",
            "appActivity": ".main.MainActivity",
            "noReset": "True",
            "unicodeKeyboard": "True",
            "resetKeyboard": "True"
        }
        self.server = 'http://localhost:4723/wd/hub'
        self.driver = webdriver.Remote(self.server, self.desired_caps)
        self.last_user = ''
    def comments(self):
        sleep(5)
    
    def tapSearch(self, keyword):
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/ie').click()
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/ie').send_keys(keyword)
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/a8j').click()
    def downSwipe_m(self):
        self.driver.swipe(430, 1500, 430, 800)
    def downSwipe_s(self):
        self.driver.swipe(430, 1500, 430, 1400)

    def findAUser_user(self):
        while True:
            try:
                try:
                    user = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/b7d')
                except:
                    self.downSwipe_s()
                    continue
                if not operator.eq(user.get_attribute('text'), self.last_user):
                    self.last_user = user.get_attribute('text')
                    return user
                else:
                    self.downSwipe_s()
                    continue
            except:
                print('find user error swipe')
                continue
    def findAUser_m(self):
        while True:
            try:
                try:
                    user = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/a_o')
                except:
                    self.downSwipe_m()
                    continue
                if not operator.eq(user.get_attribute('text'), self.last_user):
                    self.last_user = user.get_attribute('text')
                    return user
                else:
                    self.downSwipe_m()
                    continue
            except:
                print('find user error swipe')
                continue

    def tapUser(self, user):
        user.click()
        try:
            els = self.driver.find_elements_by_id('com.ss.android.ugc.aweme:id/title')
            self.el = None
            for e in els:
                if operator.contains(e.get_attribute('text'), '作品'):
                    self.el = e
            if self.el == None:
                self.driver.keyevent(4)
                return
            elm_fans = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/a_9')
            elm_fans_text = elm_fans.get_attribute('text')
            if elm_fans_text.find('.') == -1:
                self.driver.keyevent(4)
                return
            else:
                wan_count = re.sub(r'\..*', '', elm_fans_text)
                if int(wan_count) < 9:
                    self.driver.keyevent(4)
                    return
            self.el.click()
            class_text = '//android.widget.TextView[@text="暂时没有更多了"]'
            class_text_fail = '//android.widget.TextView[@text="加载失败，点击重试"]'
            while True:
                f = self.driver.find_elements_by_xpath(class_text_fail)
                if len(f) == 0:
                    l = self.driver.find_elements_by_xpath(class_text)
                    if len(l) == 0:
                        self.downSwipe_m()
                        continue
                    else:
                        self.driver.keyevent(4)
                        break
                else:
                    f[0].click()
        except:
            print('tap user error')
            self.driver.keyevent(4)

 
    def swipe2left(self):
        self.driver.swipe(250, 1000, 1000, 1000)


    def search_multiple(self, keyword:str):
        self.comments()
        self.swipe2left()
        self.tapSearch(keyword)
        #self.tapSearch(u'我叫Abbily')
        sleep(5)
        while True:
            element = self.findAUser_m()
            self.tapUser(element)
    def search_user(self, keyword:str):
        self.comments()
        self.swipe2left()
        self.tapSearch(keyword)
        class_text = '//android.widget.TextView[@text="用户"]'
        self.driver.find_elements_by_xpath(class_text)[0].click()
        sleep(5)
        while True:
            element = self.findAUser_user()
            self.tapUser(element)
    def collect_catagory(self):
        self.comments()
        self.swipe2left()
        sleep(5)
        while True:
            self.downSwipe_m()
    def search_video(self, keyword):
        self.comments()
        self.swipe2left()
        self.tapSearch(keyword)
        class_text = '//android.widget.TextView[@text="视频"]'
        self.driver.find_elements_by_xpath(class_text)[0].click()
        sleep(5)
        while True:
            self.downSwipe_m()


if __name__ == '__main__':
    action = Action()
    #action.throught_multiple(u'长腿')
    #action.throught_user(u'美食')
    #action.collect_catagory()
    action.search_video(u'红烧肉')