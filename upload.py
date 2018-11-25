import subprocess
import os
import re
import time
import sys, getopt

xjj_dir = '/Users/yijian/Desktop/dy_video'
ms_dir = '/Users/yijian/Desktop/ms_video'

def upload(source_dir:str):
    list = os.listdir(source_dir)
    for i in range(0, len(list)):
        path = os.path.join(source_dir, list[i])
        if os.path.isfile(path):
            if list[i].endswith('.mp4'):
                text_path = re.sub('.mp4','.text', path)
                with open(text_path) as f:
                    title = f.readline()
                    title = re.sub('\n', '', title)
                    desc = f.readline()
                    desc = re.sub('\n', '', desc)
                    sub = ""
                    if source_dir.find('dy_video') != -1:
                        #sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_dy.json --title=\"" + title + "\" --description=\"" + desc + "\" --tags=\"抖音,抖音 app,抖音短视频,vibrato,抖音歌,抖音视频,音乐,music,抖音影片,最爱抖音,dj抖音,短视频,台湾正妹,台湾,tik tok,美眉,美女,正妹,如何玩抖音,怎样玩抖音,抖音美女,抖音正妹,靓妹,抖音靓妹,文艺,经典,二次元,恋爱,青春,自拍,如何自拍,帅气自拍,抖音教程,经典音乐,经典歌曲,流行歌曲,流行音乐,热门歌曲,热门音乐,搞笑,萌,懵,女神,dream you,抖音音乐,排行榜,抖音排行榜,抖音收藏夹,特效,数码,视频,可爱,全民星,全明星,小姐姐,洗脑神曲,手势舞,萌妹子,热门,合集,网红,panama,抖音怎么玩,抖音 爱的就是你,好玩,best song,bgm,抖音教學 how to love,抖音 老大,抖音 海草,tik tok app\" " + path
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_dy.json --title=\"" + title + "\" --tags=\"抖音,抖音 app,抖音短视频,vibrato,抖音歌,抖音视频,音乐,music,抖音影片,最爱抖音,dj抖音,短视频,台湾正妹,台湾,tik tok,美眉,美女,正妹,如何玩抖音,怎样玩抖音,抖音美女,抖音正妹,靓妹,抖音靓妹,文艺,经典,二次元,恋爱,青春,自拍,如何自拍,帅气自拍,抖音教程,经典音乐,经典歌曲,流行歌曲,流行音乐,热门歌曲,热门音乐,搞笑,萌,懵,女神,dream you,抖音音乐,排行榜,抖音排行榜,抖音收藏夹,特效,数码,视频,可爱,全民星,全明星,小姐姐,洗脑神曲,手势舞,萌妹子,热门,合集,网红,panama,抖音怎么玩,抖音 爱的就是你,好玩,best song,bgm,抖音教學 how to love,抖音 老大,抖音 海草,tik tok app\" " + path
                    elif source_dir.find('ms_video') != -1:
                        #sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ms.json --title=\"" + title + "\" --description=\"" + desc + "\" --tags=\"中国菜, 美食, foodvideo, food, chinese, cuisine, 料理百科, 达人厨房, cooking, kitchen\" " + path
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ms.json --title=\"" + title +  "\" --tags=\"中国菜, 美食, foodvideo, food, chinese, cuisine, 料理百科, 达人厨房, cooking, kitchen\" " + path
                    elif source_dir.find('ys_video') != -1:
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ys.json --title=\"" + title +  "\" --tags=\"历史, 军事, 政治, 野史, 外星人, 美国, 契约, 工程师, Phil Schneider, 特种部队, 摄影, 蜥蜴人, 克隆, 实验\" " + path
                    elif source_dir.find('xm_video') != -1:
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_xm.json --title=\"" + title +  "\" --tags=\"熊猫, 萌, 萌宠, 卡哇伊, 卖萌, panda, 胖达君, 胖达, 肥仔, 团团\" " + path
                    elif source_dir.find('jk_video') != -1:
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_jk.json --title=\"" + title +  "\" --tags=\"养生 健康\" " + path
                    print(sub)
                    subprocess.check_call(args=sub, shell=True)
                    print(list[i])
                    os.remove(path)

def apath(path:str):
    if path.startswith('.'):
        return os.path.abspath(path)
    elif path.startswith('~'):
        home = os.path.expanduser('~')
        return re.sub('~', home, path)
    else:
        return path

def main(argv):
    sdir = ""

    try:
        # 这里的 h 就表示该选项无参数，i:表示 i 选项后需要有参数
        opts, args = getopt.getopt(argv, "hi:",["indir="])
    except getopt.GetoptError:
        print('Error: upload.py param')
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print('Error: upload.py param')
            sys.exit()
        elif opt in ("-i", "--indir"):
            sdir = apath(arg)

    print('indir: ', sdir)
    upload(sdir)


if __name__ == '__main__':
     main(sys.argv[1:])
