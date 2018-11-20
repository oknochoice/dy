import os,shutil
import sqlite3

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

dstdir = '/Users/yijian/Desktop/dy_video'
srcdir = '/Volumes/data/video'
uid = '24058267831'

if __name__ == '__main__':
    conn = sqlite3.connect('dy.db')
    item_list = conn.execute('select md5,ts from t_videos where uid = ?', (uid,)).fetchall()
    for item in item_list:
        print(item)
        s_file = srcdir + "/" + item[0] + '.mp4'
        d_file = dstdir + "/" + str(item[1]) + '.mp4'
        mycopyfile(s_file, d_file)
        


