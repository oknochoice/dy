import acoustid
import chromaprint
import sqlite3
import os
import logging
import sys, getopt, re
import time, datetime
import subprocess
import hashlib
import shutil
import json
import traceback

class Sql_dy:
    def __init__(self):
        logging.debug('%s begin', __class__)
        self.dy = sqlite3.connect('dy.db')
        self.acoust = sqlite3.connect('acoust.db')
        self.acoust.execute("create table if not exists t_dy_video_audio (" 
                          "id integer primary key autoincrement, "
                          "video_name text unique not null, "
                          "music_md5 text not null"
                          ")")
        self.acoust.execute("create table if not exists t_dy_audio_finger (" 
                          "id integer primary key autoincrement, "
                          "music_md5 text unique not null, "
                          "finger text not null"
                          ")")
        self.acoust.commit()
    def __del__(self):
        logging.debug('%s begin', __class__)
        self.acoust.close()
    def insertVideoMusicMd5(self, video_name: str, md5:str):
        sql = '''insert or replace into t_dy_video_audio (video_name, music_md5) values (?,?)'''
        self.acoust.execute(sql, (video_name, md5))
        self.acoust.commit()

class Singleton_sql:
    instance = None
    @staticmethod
    def get_instance():
        logging.debug('begin')
        if Singleton_sql.instance is None:
            logging.debug('init')
            Singleton_sql.instance = Sql_dy()
        return Singleton_sql.instance

acoust_info = dict()

def get_acoust_info():
    json_path = os.path.join(source_dir, 'acoust.json')
    global acoust_info
    if not os.path.exists(json_path):
        acoust_info['last_time_op'] = 0
        set_acoust_info()
    with open(json_path, 'r') as f:
        acoust_info = json.load(f)



def set_acoust_info():
    json_path = os.path.join(source_dir, 'acoust.json')
    global acoust_info
    with open(json_path, 'w') as f:
        json.dump(acoust_info, f)


    
def apath(path:str):
    if path.startswith('.'):
        return os.path.abspath(path)
    elif path.startswith('~'):
        home = os.path.expanduser('~')
        return re.sub('~', home, path)
    else:
        return path

def extract_video_info(indir: str, audio_dir: str):
    files = os.listdir(indir)
    for i in range(0, len(files)):
        path = os.path.join(indir, files[i])
        if (os.path.isfile(path) and
            path.endswith('mp4') and
            os.path.getctime(path) > acoust_info['last_time_op']):
            sub = 'ffmpeg -y -i ' + path + ' temp.wav'
            hash_text = 'error'
            try:
                subprocess.check_call(args=sub, shell=True)
                with open('temp.wav', 'rb') as f:
                    md5 = hashlib.md5()
                    md5.update(f.read())
                    hash_text = md5.hexdigest()
                print(hash_text)
                d_path = os.path.join(audio_dir, hash_text) + '.wav'
                shutil.move('temp.wav', d_path)
            except :
                print(traceback.format_exc())
            Singleton_sql.get_instance().insertVideoMusicMd5(files[i], hash_text)

def extract_music_info(indir: str):
    files = os.listdir(indir)


source_dir = "./"
def main(argv):
    global source_dir
    audio_dir = ""

    try:
        # 这里的 h 就表示该选项无参数，i:表示 i 选项后需要有参数
        opts, args = getopt.getopt(argv, "hi:",["indir="])
    except getopt.GetoptError:
        print('Error: args')
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print('Error: args')
            sys.exit()
        elif opt in ("-i", "--indir"):
            source_dir = apath(arg)
            audio_dir = os.path.join(source_dir, '-audio')
            if not os.path.exists(audio_dir):
                os.mkdir(audio_dir)

    print('sourcedir: ', source_dir)
    get_acoust_info()
    extract_video_info(source_dir, audio_dir)
    set_acoust_info()

if __name__ == '__main__':
    main(sys.argv[1:])