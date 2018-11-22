import subprocess
import os
import re
import time

if __name__ == '__main__':
    rootdir = '/Users/yijian/Desktop/dy_video'
    list = os.listdir(rootdir)
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isfile(path):
            if list[i].endswith('.mp4'):
                text_path = re.sub('.mp4','.text', path)
                with open(text_path) as f:
                    title = f.readline()
                    title = re.sub('\n', '', title)
                    desc = f.readline()
                    desc = re.sub('\n', '', desc)
                    sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --title=\"" + title + "\" --description=\"" + desc + "\" --tags=\"抖音,抖音 app,抖音短视频,vibrato,抖音歌,抖音视频,音乐,music,抖音影片,最爱抖音,dj抖音,短视频,台湾正妹,台湾,tik tok,美眉,美女,正妹,如何玩抖音,怎样玩抖音,抖音美女,抖音正妹,靓妹,抖音靓妹,文艺,经典,二次元,恋爱,青春,自拍,如何自拍,帅气自拍,抖音教程,经典音乐,经典歌曲,流行歌曲,流行音乐,热门歌曲,热门音乐,搞笑,萌,懵,女神,dream you,抖音音乐,排行榜,抖音排行榜,抖音收藏夹,特效,数码,视频,可爱,全民星,全明星,小姐姐,洗脑神曲,手势舞,萌妹子,热门,合集,网红,panama,抖音怎么玩,抖音 爱的就是你,好玩,best song,bgm,抖音教學 how to love,抖音 老大,抖音 海草,tik tok app\" " + path
                    subprocess.check_call(args=sub, shell=True)
                    print(list[i])
                    os.remove(path)

