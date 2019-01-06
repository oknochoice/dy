import os,shutil
import sqlite3
import json
import subprocess
import sys, getopt, re

def mycopyfile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!",srcfile)
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        print("destination dirname %s filename %s", fpath, fname)
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.copyfile(srcfile,dstfile)      #复制文件
        print("%s --> %s", srcfile, dstfile)

def sortVideo(t: tuple):
    statistics = json.loads(t[1])
    return statistics['order_no']

srcdir = '/Volumes/data/xmly_video'

def extract_video(uid:str, dstdir:str):
    water_used = ""
    info = dict()
    with open("./banyun.json", "r") as f:
        info = json.load(f)
        water_used = info[uid]["water"]
    l_srcdir = srcdir + '/' + uid
    conn = sqlite3.connect('dyNew.db')
    item_all_video = conn.execute('select md5,statistics from t_videos_xmly where uid = ? and isUploaded == 0', (uid,)).fetchall()
    item_all_video_sorted = sorted(item_all_video, key = sortVideo)
    for item in item_all_video_sorted:
        s_file = l_srcdir + "/" + item[0] + '.mp3'
        statistics = json.loads(item[1])
        d_file_mp4 = dstdir + "/" + str(statistics['order_no']) + '-' + item[0] + '.mp4'
        d_file_text = dstdir + "/" + str(statistics['order_no']) + '-' + item[0] + '.text'
        logstr = statistics['title'] + '\n' + uid + '\n'
        print(logstr)
        print(info[uid]["playlist"])
        video_title = re.sub(r'[：•·:|\-\?+,，。？！]', '\n',statistics['title'])
        video_title = re.sub(r'["\';]', '',video_title)
        print(video_title)
        sub = "ffmpeg -y -threads 4 -loop 1 -i ./" + water_used + " -i " + s_file + " -vf drawtext=\"fontfile=./fz.ttf:text=石马Beautiful:fontcolor=white:fontsize=40\",drawtext=\"fontfile=./fz.ttf:text=" + video_title + ":fontcolor=green:fontsize=100:x=0:y=h-th\" -shortest -s 1280x720 -r 30 " + d_file_mp4
        print(sub)
        subprocess.check_call(args=sub, shell=True)
        with open(d_file_text, "w") as f:
            f.write(logstr)
            f.flush()
        conn.execute("update t_videos_xmly set isUploaded = 1 where uid = ? and md5 = ?", (uid,item[0]))
        conn.commit()
    conn.close()
def apath(path:str):
    if path.startswith('.'):
        return os.path.abspath(path)
    elif path.startswith('~'):
        home = os.path.expanduser('~')
        return re.sub('~', home, path)
    else:
        return path

def main(argv):
    uid = ""
    outdir = ""
    global srcdir

    try:
        # 这里的 h 就表示该选项无参数，i:表示 i 选项后需要有参数
        opts, args = getopt.getopt(argv, "hu:o:",["uid=", "outdir="])
    except getopt.GetoptError:
        print('Error: test_arg.py -i <uid> -o <outdir>')
        print('   or: test_arg.py --uid=<:uid> --outdir=<outdir>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print('Error: test_arg.py -i <uid> -o <outdir>')
            print('   or: test_arg.py --uid=<uid> --outdir=<outdir>')
            sys.exit()
        elif opt in ("-u", "--uid"):
            uid = arg
        elif opt in ("-o", "--outdir"):
            outdir = apath(arg)

    print('uid : ', uid)
    print('sourcedir: ', srcdir)
    print('outdir: ', outdir)
    if int(uid) == 0:
        with open("./banyun.json", "r") as f:
            info = json.load(f)
            for key in info:
                print(key)
                extract_video(key, outdir)
    else:
        extract_video(uid, outdir)

if __name__ == '__main__':
    main(sys.argv[1:])


