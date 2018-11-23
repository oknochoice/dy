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

srcdir = '/Volumes/data/video'
def extract_video(uid:str, dstdir:str):
    conn = sqlite3.connect('dy.db')
    user = conn.execute('select location, nickname, mplatform_followers_count from t_users where uid = ?', (uid,)).fetchone()
    location = user[0]
    nickname = user[1]
    followers_count = str(user[2])
    for item in conn.execute('select md5,ts,statistics,other from t_videos where uid = ?', (uid,)):
        s_file = srcdir + "/" + item[0] + '.mp4'
        d_file_mp4 = dstdir + "/" + str(item[1]) + '-' + item[0] + '.mp4'
        d_file_text = dstdir + "/" + str(item[1]) + '-' + item[0] + '.text'
        statistics = json.loads(item[2])
        digg_count = str(statistics['digg_count'])
        share_count = str(statistics['share_count'])
        comment_count = str(statistics['comment_count'])
        other = json.loads(item[3])
        share_title = other['share_info']['share_title']
        logstr = share_title + "\n" + \
                "坐标:" + location + ", " + nickname + ", 粉量:" + followers_count + \
                "赞有:" + digg_count + ",分享量:" + share_count + ",评论量:" + comment_count + "\n"
        print(logstr)
        sub = "ffmpeg -i " + s_file + " -i ./shima.png -filter_complex overlay=W-w " + d_file_mp4
        subprocess.check_call(args=sub, shell=True)
        with open(d_file_text, "w") as f:
            f.write(logstr)
            f.flush()
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

    try:
        # 这里的 h 就表示该选项无参数，i:表示 i 选项后需要有参数
        opts, args = getopt.getopt(argv, "hu:o:",["uid=", "outdir="])
    except getopt.GetoptError:
        print('Error: test_arg.py -i <uid> -o <outdir>')
        print('   or: test_arg.py --uid=<uid> --outdir=<outdir>')
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
    print('outdir: ', outdir)
    extract_video(uid, outdir)

if __name__ == '__main__':
    main(sys.argv[1:])


