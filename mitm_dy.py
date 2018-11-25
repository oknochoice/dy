from bs4 import BeautifulSoup
from mitmproxy import ctx, http, addonmanager
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
#from time import sleep
import hashlib
import requests
import sqlite3
import json
import time
import threading
import logging
import os
import traceback

class Sql_dy:
    def __init__(self):
        logging.debug('%s begin', __class__)
        self.conn = sqlite3.connect('dy.db')
        self.conn.execute("create table if not exists t_users (id integer primary key autoincrement, short_id text not null, uid text unique not null, nickname text, gender int not null, location text, mplatform_followers_count int not null, follower_count int not null, aweme_count int not null, total_favorited int not null, other text not null)")
        self.conn.execute("create index if not exists uid on t_users (uid)")
        self.conn.execute("create index if not exists short_id on t_users (short_id)")
        self.conn.execute("create index if not exists follower_count on t_users (follower_count)")
        self.conn.execute("create index if not exists aweme_count on t_users (aweme_count)")
        self.conn.execute("create table if not exists t_videos (id integer primary key autoincrement, md5 text not null, web_uri text not null, uid text not null, ts int not null, statistics text, other text, unique(uid, md5, web_uri))")
        self.conn.execute("create index if not exists web_uri on t_videos (web_uri)")
        self.conn.execute("create index if not exists md5 on t_videos (md5)")
        self.conn.execute("create table if not exists t_videos_failed (id integer primary key autoincrement, url text unique not null, web_uri text not null, uid text not null, ts int not null, statistics text)")
        self.conn.execute("create table if not exists t_user_avatars (id integer primary key autoincrement, uid text not null, md5 text not null, ts int not null, unique(uid, md5))")
        self.conn.commit()
    def __del__(self):
        logging.debug('%s begin', __class__)
        self.conn.close()
    
    def insertUser(self, para):
        logging.debug('%s begin', __class__)
        sql = '''insert or replace into t_users (short_id, uid, nickname, gender, location, mplatform_followers_count, follower_count, aweme_count , total_favorited, other) values (?,?,?,?,?,?,?,?,?,?)'''
        self.conn.execute(sql, para)
        self.conn.commit()
    def insertVideoFailed(self, para):
        logging.debug('%s begin', __class__)
        sql = '''insert or ignore into t_videos_failed (url, web_uri, uid, ts, statistics) values (?,?,?,?,?)'''
        self.conn.execute(sql, para)
        self.conn.commit()
    def insertVideo(self, para):
        logging.debug('%s begin', __class__)
        sql_del = '''delete from t_videos_failed where web_uri = ?'''
        sql = '''insert or ignore into t_videos (md5, web_uri, uid, ts, statistics, other) values (?,?,?,?,?,?)'''
        self.conn.execute(sql_del, (para[1],))
        self.conn.execute(sql, para)
        self.conn.commit()
    def insertAvatars(self, para):
        logging.debug('%s begin', __class__)
        sql = '''insert or ignore into t_user_avatars (md5, uid, ts) values(?,?,?)'''
        self.conn.execute(sql, para)
        self.conn.commit()
    def isVideoExist(self, para) -> bool:
        logging.debug('%s begin', __class__)
        sql = '''select web_uri from t_videos where web_uri = ?'''
        res = self.conn.execute(sql, para).fetchone()
        if res is None:
            return False
        else:
            return True
    def queryUser_follower(self, uid):
        sql = '''select mplatform_followers_count from t_users where uid = ?'''
        user = self.conn.execute(sql, (uid,)).fetchone()
        if user == None:
            return 0
        else:
            return user[0]


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
        def __init__(self, url, web_uri, uid, ts, statistics, other, if_ge: int):
            logging.debug('%s begin', __class__)
            self.url = url
            self.web_uri = web_uri
            self.other = other
            self.uid = uid
            self.ts = ts
            self.statistics = statistics
            self.if_ge = if_ge
        def run(self):
            logging.debug('%s begin', __class__)
            follower_count = Singleton_sql.get_instance().queryUser_follower(self.uid)
            logging.info('if_ge %d, followercount %d', self.if_ge, follower_count)
            if follower_count < self.if_ge:
                return
            if Singleton_sql.get_instance().isVideoExist((self.web_uri,)):
                logging.info('%s video is exist, web_uri: %s', __class__, self.web_uri)
                pass
            else:
                try:
                    #res = requests.get(self.url, stream = True, timeout = 5)
                    s = requests.Session()
                    s.mount('http://', HTTPAdapter(max_retries=5))
                    s.mount('https://', HTTPAdapter(max_retries=5))
                    res = s.get(self.url, stream = True, timeout=5)
                    md5 = hashlib.md5()
                    md5.update(res.content)
                    filename = md5.hexdigest() + '.mp4'
                    path = '/Volumes/data/video/' + filename
                    with open(path,  'wb') as f:
                        f.write(res.content)
                        f.flush()
                    param = (md5.hexdigest(), self.web_uri, self.uid, self.ts, self.statistics, self.other)
                    logging.info(param.__str__())
                    Singleton_sql.get_instance().insertVideo(param)
                except:
                    logging.warning('download video failure:%s', self.url)
                    Singleton_sql.get_instance().insertVideoFailed((self.url, self.web_uri, self.uid, self.ts, self.statistics))
        def desc(self):
            return 'video:' + self.url
    class Avatar(Source):
        def __init__(self, url, uid):
            logging.debug('%s begin', __class__)
            self.url = url
            self.uid = uid
        def run(self):
            logging.debug('%s begin', __class__)
            try:
                avatar_res = requests.get(self.url, stream = True, timeout = 3)
                file_suffix = os.path.splitext(self.url)[1]
                md5 = hashlib.md5()
                md5.update(avatar_res.content)
                path = '/Volumes/data/avatar/' + md5.hexdigest() + file_suffix
                with open(path, 'ab') as f:
                    f.write(avatar_res.content)
                    f.flush()
                avatar_t = (md5.hexdigest(), self.uid, int(time.time()))
                Singleton_sql.get_instance().insertAvatars(avatar_t)
            except:
                logging.warning('avatar download failure:%s', self.url)
        def desc(self):
            return 'avatar:' + self.url
    class Userinfo(Source):
        def __init__(self, ui):
            logging.debug('%s begin', __class__)
            self.user_info = ui
        def run(self):
            logging.debug('%s begin', __class__)
            Singleton_sql.get_instance().insertUser(self.user_info)
        def desc(self):
            return 'user:' + self.user_info.__str__()
    def __init__(self):
        logging.debug('%s begin', __class__)
        self.con = threading.Condition(threading.Lock())
        self.source = []
    def addTasks(self, tasks:list, isBegin = False):
        logging.debug('%s begin', __class__)
        self.con.acquire()
        if isBegin == True:
            self.source[0:0] = tasks
        else:
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
                logging.info('working current tasks num is %d', len(self.source))
                self.current_task = self.source[0]
                self.source.pop(0)
                self.con.release()
            else:
                logging.info('waiting current tasks num is %d', len(self.source))
                self.con.wait()
                self.con.release()
                continue
            logging.info(self.current_task.desc())
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
        ctx.log.alert('load begin')
        logging.getLogger('').handlers = []
        log_format = "[%(asctime)s:%(levelname)s:%(thread)d:%(filename)s:%(lineno)d:%(funcName)s]%(message)s"
        logging.basicConfig(filename='my.log', level=logging.INFO, format=log_format)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("wsgi").setLevel(logging.WARNING)
        logging.debug('%s log init test', __class__)
    def response(self, flow: http.HTTPFlow) -> None:
        logging.info('in %s',flow.request.url)
        #if (flow.request.url.startswith('https://aweme-eagle.snssdk.com/aweme/v1/user') or
        #    flow.request.url.startswith('https://aweme.snssdk.com/aweme/v1/user')):
        if flow.request.url.find('/aweme/v1/user/') != -1:
            try:
                logging.info('user info url %s',flow.request.url)
                # insert user
                data = json.loads(flow.response.get_text())
                user = data['user']
                user_info = (user['short_id'], user['uid'], user['nickname'], user['gender'], user['location'], user['mplatform_followers_count'], user['follower_count'], user['aweme_count'], user['total_favorited'], json.dumps(user))
                u_task = DownloadThread.Userinfo(user_info)
                Singleton_tread.get_instance().addTasks([u_task], True)
                # insert avatar
                avatar_url = user['avatar_larger']['url_list'][0]
                a_task = DownloadThread.Avatar(avatar_url, user['uid'])
                Singleton_tread.get_instance().addTasks([a_task])
            except:
                logging.error('user info error: url %s', flow.request.url)
        if flow.request.url.find('/aweme/v1/aweme/post/') != -1:
            try:
                logging.info('user produce url %s',flow.request.url)
                res_dict = json.loads(flow.response.get_text())
                fields = flow.request.query.fields
                for tt in enumerate(fields):
                    if tt[1][0] == 'user_id':
                        self.uid = tt[1][1]
                    elif tt[1][0] == 'ts':
                        self.ts = tt[1][1]
                video_list = res_dict['aweme_list']
                videos = []
                for video in enumerate(video_list):
                    try:
                        url = video[1]['video']['play_addr']['url_list'][0]
                        uri = video[1]['video']['play_addr']['uri']
                        statistics = video[1]['statistics']
                        v = DownloadThread.Video(url, uri, self.uid, self.ts, json.dumps(statistics), json.dumps(video[1]), 94000)
                        videos.append(v)
                    except:
                        continue
                Singleton_tread.get_instance().addTasks(videos)
            except:
                logging.error('video list info error: %s', traceback.format_exc())


addons = [
    UserInfoer()
]