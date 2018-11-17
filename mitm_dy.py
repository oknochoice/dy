from bs4 import BeautifulSoup
from mitmproxy import ctx, http, addonmanager
from urllib.parse import urlparse
import hashlib
import requests
import sqlite3
import json
import time
import threading
import logging

class Sql_dy:
    def __init__(self):
        self.conn = sqlite3.connect('dy.db')
        self.conn.execute("create table if not exists t_users (id integer primary key autoincrement, short_id text not null, uid text unique not null, nickname text, gender int not null, location text, following_count int not null, follower_count int not null, aweme_count int not null, total_favorited int not null)")
        self.conn.execute("create index if not exists uid on t_users (uid)")
        self.conn.execute("create index if not exists short_id on t_users (short_id)")
        self.conn.execute("create index if not exists follower_count on t_users (follower_count)")
        self.conn.execute("create index if not exists aweme_count on t_users (aweme_count)")
        self.conn.execute("create table if not exists t_videos (id integer primary key autoincrement, md5 text not null, web_hash text not null, uid text not null, ts int not null, statistics text, unique(uid, md5, web_hash))")
        self.conn.execute("create index if not exists web_hash on t_videos (web_hash)")
        self.conn.execute("create index if not exists md5 on t_videos (md5)")
        self.conn.execute("create table if not exists t_videos_failed (id integer primary key autoincrement, url text unique not null, web_hash text not null, uid text not null, ts int not null, statistics text)")
        self.conn.execute("create table if not exists t_user_avatars (id integer primary key autoincrement, uid text not null, md5 text not null, ts int not null, unique(uid, md5))")
        self.conn.commit()
    def __del__(self):
        Sql_dy.conn.close()
    
    def insertUser(self, para):
        sql = '''insert or replace into t_users (short_id, uid, nickname, gender, location, following_count, follower_count, aweme_count , total_favorited) values (?,?,?,?,?,?,?,?,?)'''
        self.conn.execute(sql, para)
        self.conn.commit()
    def insertVideoFailed(self, para):
        sql = '''insert or ignore into t_videos_failed (url, web_hash, uid, ts, statistics) values (?,?,?,?,?)'''
        self.conn.execute(sql, para)
        self.conn.commit()
    def insertVideo(self, para):
        sql_del = '''delete from t_videos_failed where web_hash = ?'''
        sql = '''insert or ignore into t_videos (md5, web_hash, uid, ts, statistics) values (?,?,?,?,?)'''
        self.conn.execute(sql_del, (para[1]))
        self.conn.execute(sql, para)
        self.conn.commit()
    def insertAvatars(self, para):
        sql = '''insert or ignore into t_user_avatars (md5, uid, ts) values(?,?,?)'''
        self.conn.execute(sql, para)
        self.conn.commit()
    def isVideoExist(self, para) -> bool:
        sql = '''select web_hash from t_videos where web_hash = ?'''
        res = self.conn.execute(sql, para).fetchone()
        if res is None:
            return False
        else:
            return True


class Singleton_sql:
    instance = None
    @staticmethod
    def get_instance():
        logging.debug('begin')
        if Singleton_sql.instance is None:
            logging.debug('init')
            Singleton_sql.instance = Sql_dy()
        return Singleton_sql.instance

class DownloadThread:
    class Source:
        def run(self):
            logging.debug('%s begin', __class__)
    class Video(Source):
        def __init__(self, url, webhash, uid, ts, statistics):
            logging.debug('%s begin', __class__)
            self.url = url
            self.webhash = webhash
            self.uid = uid
            self.ts = ts
            self.statistics = statistics
        def run(self):
            logging.debug('%s begin', __class__)
            if Singleton_sql.get_instance().isVideoExist(self.webhash):
                pass
            else:
                try:
                    res = requests.get(self.url, stream = True, timeout = 5)
                except:
                    Singleton_sql.get_instance().insertVideoFailed((self.url, self.webhash, self.uid, self.ts, self.statistics))
                md5 = hashlib.md5()
                md5.update(res.content)
                filename = md5.hexdigest() + '.mp4'
                path = '/Volumes/data/video/' + filename
                with open(path,  'ab') as f:
                    f.write(res.content)
                    f.flush()
                param = (md5.hexdigest(), self.webhash, self.uid, self.ts, self.statistics)
                Singleton_sql.get_instance().insertVideo(param)
    class Avatar(Source):
        def __init__(self, url, uid):
            logging.debug('%s begin', __class__)
            self.url = url
            self.uid = uid
        def run(self):
            logging.debug('%s begin', __class__)
            avatar_res = requests.get(self.url, stream = True)
            md5 = hashlib.md5()
            md5.update(avatar_res.content)
            path = '/Volumes/data/avatar/' + md5.hexdigest() + '.jpeg'
            with open(path, 'ab') as f:
                f.write(avatar_res.content)
                f.flush()
            avatar_t = (md5.hexdigest(), self.uid, int(time.time()))
            Singleton_sql.get_instance().insertAvatars(avatar_t)
    class Userinfo(Source):
        def __init__(self, ui):
            logging.debug('%s begin', __class__)
            self.user_info = ui
        def run(self):
            logging.debug('%s begin', __class__)
            Singleton_sql.get_instance().insertUser(self.user_info)
    def __init__(self):
        logging.debug('%s begin', __class__)
        self.con = threading.Condition(threading.Lock())
        self.source = []
    def addTasks(self, tasks:list):
        logging.debug('%s begin', __class__)
        self.con.acquire()
        self.source += tasks
        logging.debug('task %d', len(tasks))
        logging.debug('source %d', len(self.source))
        self.con.notify()
        self.con.release()
    def run(self):
        logging.debug('%s begin', __class__)
        while True:
            logging.debug('loop begin')
            self.con.acquire()
            if len(self.source) != 0:
                logging.debug('pick a task %d', len(self.source))
                self.current_task = self.source[0]
                self.source.pop(0)
                self.con.release()
            else:
                logging.debug('waiting %d', len(self.source))
                self.con.wait()
                self.con.release()
                continue
            logging.debug('working %d', len(self.source))
            self.current_task.run()

class Singleton_tread:
    instance = None
    @staticmethod
    def get_instance():
        if Singleton_tread.instance is None:
            Singleton_tread.instance = DownloadThread()
            t = threading.Thread(target=Singleton_tread.instance.run, daemon=True)
            t.start()
        return Singleton_tread.instance


    
class TrackRecorder:
    def response(self, flow: http.HTTPFlow) -> None:
        #ctx.log.info('track record running ------------------------------')
        if flow.request.url.find('ixigua.com') != -1:
            res = requests.get(flow.request.url, stream = True)
            md5 = hashlib.md5()
            md5.update(res.content)
            filename = md5.hexdigest() + '.mp4'
            path = '/Volumes/data/temp/' + filename
            ctx.log.info(path)
            with open(path,  'ab') as f:
                f.write(res.content)
                f.flush()

class UserInfoer:
    def load(self, entry: addonmanager.Loader):
        log_format = "[%(asctime)s:%(levelname)s:%(thread)d:%(filename)s:%(lineno)d:%(funcName)s]%(message)s"
        logging.basicConfig(filename='my.log', level=logging.DEBUG, format=log_format)
        logging.debug('%slog init test', __class__)
    def response(self, flow: http.HTTPFlow) -> None:
        #ctx.log.info('userinfo runing -------------------------------')
        #ctx.log.info(flow.request.url)
        if (flow.request.url.startswith('https://aweme-eagle.snssdk.com/aweme/v1/user') or
            flow.request.url.startswith('https://aweme.snssdk.com/aweme/v1/user')):
            # insert user
            data = json.loads(flow.response.get_text())
            user = data['user']
            user_info = (user['short_id'], user['uid'], user['nickname'], user['gender'], user['location'], user['following_count'], user['follower_count'], user['aweme_count'], user['total_favorited'])
            ctx.log.info(user_info.__str__())
            u_task = DownloadThread.Userinfo(user_info)
            Singleton_tread.get_instance().addTasks([u_task])
            # insert avatar
            avatar_url = user['avatar_larger']['url_list'][0]
            a_task = DownloadThread.Avatar(avatar_url, user['uid'])
            Singleton_tread.get_instance().addTasks([a_task])
        if flow.request.url.find('/aweme/v1/aweme/post/') != -1:
            #ctx.log.info('-------------------------------')
            #ctx.log.info(flow.request.query.fields.__str__())
            ctx.log.info(flow.request.url)
            res_dict = json.loads(flow.response.get_text())
            #ctx.log.info(flow.request.url)
            fields = flow.request.query.fields
            #ctx.log.info(fields.__str__())
            for tt in enumerate(fields):
                #ctx.log.info(tt.__str__())
                if tt[1][0] == 'user_id':
                    self.uid = tt[1][1]
                elif tt[1][0] == 'ts':
                    self.ts = tt[1][1]
            ctx.log.info(self.uid)
            ctx.log.info(self.ts)
            video_list = res_dict['aweme_list']
            videos = []
            for video in enumerate(video_list):
                url = video[1]['video']['play_addr']['url_list'][0]
                urlDict = urlparse(url)
                statistics = video[1]['statistics']
                v = DownloadThread.Video(url, urlDict.path, self.uid, self.ts, json.dumps(statistics))
                videos.append(v)
            Singleton_tread.get_instance().addTasks(videos)


addons = [
    UserInfoer()
]