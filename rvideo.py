import subprocess
import os
import re
import time


if __name__ == '__main__':
    todir = '/Users/yijian/Desktop/dy_video'
    rootdir = '/Users/yijian/Desktop/dy_video_horizontal'
    list = os.listdir(rootdir)
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        topath = os.path.join(todir, list[i])
        if os.path.isfile(path):
            if list[i].endswith('.mp4'):
                sub = "ffmpeg -i " + path + " -vf transpose=2 " + topath
                subprocess.check_call(args=sub, shell=True)
                print(list[i])

