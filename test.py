import re
import urllib
import requests
import ffmpeg

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
def ffmpeg_test():
    pass


if __name__ == "__main__":
    ffmpeg_test()