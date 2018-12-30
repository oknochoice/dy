import os,shutil
import sqlite3
import json
import subprocess
import sys, getopt, re

def mycopyfile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        print("destination dirname %s filename %s"% (fpath, fname))
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.copyfile(srcfile,dstfile)      #复制文件
def mymovefile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        print("destination dirname %s filename %s"% (fpath, fname))
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.move(srcfile,dstfile)      

srcdir = '/Volumes/data/xmly_video'
def extract_video():
    conn = sqlite3.connect('dyNew.db')
    item_all_video = conn.execute('select md5,statistics,uid from t_videos_xmly').fetchall()
    for item in item_all_video:
        s_file = srcdir + "/" + item[0] + '.mp3'
        d_file = srcdir + '/' + item[2] + "/" + item[0] + '.mp3'
        print("source file: %s, destination file %s."% (s_file, d_file))
        mymovefile(s_file, d_file)
    conn.close()


if __name__ == '__main__':
    extract_video()


