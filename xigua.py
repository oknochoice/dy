#encoding=utf-8
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time

def main():
    browser = webdriver.Chrome()
    placeholder = 'https://www.ixigua.com/c/user/article/?user_id={0}&max_behot_time={1}&max_repin_time=0&count=20&page_type=0'
    user_id = '52371875039'
    placeholder_detail = 'https://www.ixigua.com/i{0}/#mid={1}'
    while True:
        max_behot_time = '0'
        addr = placeholder.format(user_id,max_behot_time)
        print(addr)
        browser.get(addr)
        soup = BeautifulSoup(browser.page_source, "lxml")
        data = soup.pre.string
        res_dict = json.loads(data)
        if not res_dict['has_more']:
            break
        max_behot_time = str(res_dict['next']['max_behot_time'])
        request_info_list = res_dict['data']
        for info in request_info_list:
            addr_detail = placeholder_detail.format(info['item_id'], user_id)
            print(addr_detail)            
            browser.get(addr_detail)
            eles = browser.find_elements_by_css_selector('head > style.vjs-styles-dimensions')
            print(len(eles))
            if len(eles) == 0:
                starts = browser.find_elements_by_css_selector('.start-btn')[0].click()
                urls = browser.find_elements_by_css_selector('div.definition > ul > li')
                print(len(urls))
                for u in urls:
                    print(u.get_attribute('url'))
                urls[-1].click()
                time.sleep(100)
            else:
                starts = browser.find_elements_by_css_selector('.vjs-big-play-button')[0].click()

        break


 
if __name__ == '__main__':
    main()