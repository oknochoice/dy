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
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/a7y').click()
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/a7y').send_keys(keyword)
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/a81').click()
    def downSwipe(self):
        self.driver.swipe(430, 1500, 430, 800)

    def findAUser(self):
        while True:
            try:
                try:
                    user = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/a_6')
                except:
                    self.downSwipe()
                    continue
                if not operator.eq(user.get_attribute('text'), self.last_user):
                    self.last_user = user.get_attribute('text')
                    return user
                else:
                    self.downSwipe()
                    continue
            except:
                print('find user error swipe')
                continue

    def tapUser(self, user):
        user.click()
        try:
            els = self.driver.find_elements_by_id('com.ss.android.ugc.aweme:id/bn')
            self.el = None
            for e in els:
                if operator.contains(e.get_attribute('text'), '作品'):
                    self.el = e
            if self.el == None:
                self.driver.keyevent(4)
                return
            elm_fans = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/a9q')
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
                        self.downSwipe()
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
    def main(self):
        self.comments()
        self.swipe2left()
        self.tapSearch(u'小姐姐')
        #self.tapSearch(u'我叫Abbily')
        sleep(5)
        while True:
            element = self.findAUser()
            self.tapUser(element)

if __name__ == '__main__':
    action = Action()
    action.main()