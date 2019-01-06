import subprocess
import os
import re
import time
import sys, getopt
import shutil
import json

uploaded_dir = '/Volumes/data/selected'

def sort_yeshi(name:str):
    print(name.split('-'))
    key = name.split('-')[0]
    if key.isdecimal():
        return int(key)
    else:
        return 0


def upload(source_dir:str, postfix:str):
    info = dict()
    with open("./banyun.json", "r") as f:
        info = json.load(f)
    list_sorted = os.listdir(source_dir)
    sub_client = ""
    if (source_dir.find('ys_video') != -1 or
        source_dir.find('msqt_video') != -1 or
        source_dir.find('hyjq_video') != -1 or
        source_dir.find('dls_video') != -1 or
        source_dir.find('video') != -1 or
        source_dir.find('syxcg_video') != -1):
        list_sorted = sorted(list_sorted, key = sort_yeshi)
        sub_client = "cp /Users/yijian/.youtube-upload-credentials.json.ys.back /Users/yijian/.youtube-upload-credentials.json"
    elif source_dir.find('ms_video') != -1:
        sub_client = "cp /Users/yijian/.youtube-upload-credentials.json.ms.back /Users/yijian/.youtube-upload-credentials.json"
    else:
        sub_client = "rm /Users/yijian/.youtube-upload-credentials.json"
    subprocess.check_call(args = sub_client, shell=True)
    for i in range(0, len(list_sorted)):
        path = os.path.join(source_dir, list_sorted[i])
        print(list_sorted[i])
        #continue
        if os.path.isfile(path):
            if list_sorted[i].endswith(postfix):
                text_path = re.sub(postfix,'.text', path)
                with open(text_path) as f:
                    title = f.readline()
                    title = re.sub('\n', '', title)
                    uid = f.readline()
                    uid = re.sub('\n', '', uid)
                    title = re.sub(r'["]', '', title)
                    print(title, uid)
                    print(info[uid]["isupload"])
                    if info[uid]["isupload"] == 0:
                        continue
                    sub = ""
                    if source_dir.find('dy_video') != -1:
                        #sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_dy.json --title=\"" + title + "\" --description=\"" + desc + "\" --tags=\"抖音,抖音 app,抖音短视频,vibrato,抖音歌,抖音视频,音乐,music,抖音影片,最爱抖音,dj抖音,短视频,台湾正妹,台湾,tik tok,美眉,美女,正妹,如何玩抖音,怎样玩抖音,抖音美女,抖音正妹,靓妹,抖音靓妹,文艺,经典,二次元,恋爱,青春,自拍,如何自拍,帅气自拍,抖音教程,经典音乐,经典歌曲,流行歌曲,流行音乐,热门歌曲,热门音乐,搞笑,萌,懵,女神,dream you,抖音音乐,排行榜,抖音排行榜,抖音收藏夹,特效,数码,视频,可爱,全民星,全明星,小姐姐,洗脑神曲,手势舞,萌妹子,热门,合集,网红,panama,抖音怎么玩,抖音 爱的就是你,好玩,best song,bgm,抖音教學 how to love,抖音 老大,抖音 海草,tik tok app\" " + path
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_dy.json --title=\"" + title + "\" --tags=\"抖音,抖音 app,抖音短视频,vibrato,抖音歌,抖音视频,音乐,music,抖音影片,最爱抖音,dj抖音,短视频,台湾正妹,台湾,tik tok,美眉,美女,正妹,如何玩抖音,怎样玩抖音,抖音美女,抖音正妹,靓妹,抖音靓妹,文艺,经典,二次元,恋爱,青春,自拍,如何自拍,帅气自拍,抖音教程,经典音乐,经典歌曲,流行歌曲,流行音乐,热门歌曲,热门音乐,搞笑,萌,懵,女神,dream you,抖音音乐,排行榜,抖音排行榜,抖音收藏夹,特效,数码,视频,可爱,全民星,全明星,小姐姐,洗脑神曲,手势舞,萌妹子,热门,合集,网红,panama,抖音怎么玩,抖音 爱的就是你,好玩,best song,bgm,抖音教學 how to love,抖音 老大,抖音 海草,tik tok app\" " + path
                    elif source_dir.find('ms_video') != -1:
                        #sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ms.json --title=\"" + title + "\" --description=\"" + desc + "\" --tags=\"中国菜, 美食, foodvideo, food, chinese, cuisine, 料理百科, 达人厨房, cooking, kitchen\" " + path
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ms.json --title=\"" + title +  "\" --tags=\"中国菜, 美食, foodvideo, food, chinese, cuisine, 料理百科, 达人厨房, cooking, kitchen\" " + path
                    elif source_dir.find('ys_video') != -1:
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ys.json --playlist=\"一说春秋\" --title=\"" + title +  "\" --tags=\"历史, 军事, 政治, 野史, 春秋, 五霸\" " + path
                        #sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ys.json --playlist=\"冷历史\" --title=\"" + title +  "\" --tags=\"历史, 军事, 政治, 野史, 趣事\" " + path
                        #sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ys.json --playlist=\"鬼叔怪谈\" --title=\"" + title +  "\" --tags=\"历史, 军事, 政治, 野史, 鬼怪, 鬼, 怪, 灵异事件\" " + path
                    elif source_dir.find('syxcg_video') != -1:
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ys.json --playlist=\"深夜小茶馆\" --title=\"" + title +  "\" --tags=\"历史, 军事, 政治, 野史, 鬼怪, 鬼, 怪, 灵异事件\" " + path
                    elif source_dir.find('msqt_video') != -1:
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ys.json --playlist=\"秘史趣谈\" --title=\"" + title +  "\" --tags=\"历史, 军事, 政治, 野史, 鬼怪, 鬼, 怪, 灵异事件\" " + path
                    elif source_dir.find('hyjq_video') != -1:
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ys.json --playlist=\"寰宇惊奇\" --title=\"" + title +  "\" --tags=\"历史, 军事, 政治, 野史, 鬼怪, 鬼, 怪, 灵异事件\" " + path
                    elif source_dir.find('dls_video') != -1:
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ys.json --playlist=\"大力史\" --title=\"" + title +  "\" --tags=\"历史, 军事, 政治, 野史, 鬼怪, 鬼, 怪, 灵异事件\" " + path
                    elif source_dir.find('xm_video') != -1:
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_xm.json --title=\"" + title +  "\" --tags=\"熊猫, 萌, 萌宠, 卡哇伊, 卖萌, panda, 胖达君, 胖达, 肥仔, 团团\" " + path
                    elif source_dir.find('jk_video') != -1:
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_jk.json --title=\"" + title +  "\" --tags=\"养生 健康\" " + path
                    elif source_dir.find('video') != -1:
                        playlist  =  info[uid]["playlist"]
                        sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=./client_ys.json --playlist=\""+ playlist + "\" --title=\"" + title +  "\" --tags=\"" + info[uid]["tags"] + "\" " + path
                    else:
                        print("source direction is illegal.")
                        return
                    print(sub)
                    subprocess.check_call(args=sub, shell=True)
                    # move back
                    l_u_d = os.path.join(uploaded_dir, info[uid]["playlist"])
                    if not os.path.exists(l_u_d):
                        os.mkdir(l_u_d)
                    d_path = os.path.join(l_u_d, list_sorted[i])
                    d_text_path = re.sub(postfix, '.text', d_path)
                    shutil.move(text_path,d_text_path)
                    shutil.move(path,d_path)

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
    postfix = ".mp4"

    try:
        # 这里的 h 就表示该选项无参数，i:表示 i 选项后需要有参数
        opts, args = getopt.getopt(argv, "hi:p:",["indir=","postfix="])
    except getopt.GetoptError:
        print('Error: upload.py param')
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print('Error: upload.py param')
            sys.exit()
        elif opt in ("-i", "--indir"):
            sdir = apath(arg)
        elif opt in ("-p", "--postfix"):
            postfix = arg

    print('indir: ', sdir)
    upload(sdir, postfix)


if __name__ == '__main__':
     main(sys.argv[1:])
