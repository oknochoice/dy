import re
import urllib
import requests

def string():
    s1 = '12.3W粉丝'
    s2 = '12.3w粉丝'
    s3 = '123W粉丝'
    s4 = '123W粉丝'
    r1 = s1.find('.')
    r2 = s2.find('.')
    r3 = s3.find('.')
    r4 = s4.find('.')
    print("%d, %d, %d, %d", r1, r2, r3, r4 )
    s1 = re.sub(r'\..*', '', s1)
    s2 = re.sub(r'\..*', '', s2)
    s3 = re.sub(r'\..*', '', s3)
    s4 = re.sub(r'\..*', '', s4)
    print("%s", s1)
    print("%s", s2)
    print("%s", s3)
    print("%s", s4)


if __name__ == "__main__":
    url = 'https://aweme.snssdk.com/aweme/v1/aweme/post/?max_cursor=0&user_id=73838190950&count=20&retry_type=no_retry&iid=51556476339&device_id=59583657372&ac=wifi&channel=yingyonghui&aid=1128&app_name=aweme&version_code=330&version_name=3.3.0&device_platform=android&ssmix=a&device_type=ZTE+V0900&device_brand=ZTE&language=zh&os_api=27&os_version=8.1.0&uuid=868353030256808&openudid=4c49c5cfadb2026c&manifest_version_code=330&resolution=1080*2040&dpi=480&update_version_code=3302&_rticket=1542732730120&ts=1542732730&js_sdk_version=1.2.2&as=a1e5631f7aabababc40733&cp=36b1b855ab49ffb8e1Ysaa&mas=0141dc5b9fda5604d7143fdb37151ddff1ccccec0c2cc646864686'
    url_o = urllib.parse.urlsplit(url)
    param = dict(urllib.parse.parse_qsl(url_o.query))
    http = url_o.scheme + "://" + url_o.hostname + url_o.path
    http = http[0:-1]
    res = requests.get(http, params=param)
    print(res.request)
    print(res.text)