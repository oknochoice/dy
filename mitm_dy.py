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
import re
import time
import pymongo
import datetime

class Sql_dy:
    def __init__(self):
        logging.debug('%s begin', __class__)
        self.conn = sqlite3.connect('dyNew.db')
        self.conn.execute("create table if not exists t_users (id integer primary key autoincrement, short_id text not null, uid text unique not null, nickname text, gender int not null, location text, mplatform_followers_count int not null, follower_count int not null, aweme_count int not null, total_favorited int not null)")
        self.conn.execute("create index if not exists uid on t_users (uid)")
        self.conn.execute("create index if not exists short_id on t_users (short_id)")
        self.conn.execute("create index if not exists follower_count on t_users (follower_count)")
        self.conn.execute("create index if not exists aweme_count on t_users (aweme_count)")
        self.conn.execute("create table if not exists t_videos (id integer primary key autoincrement, md5 text not null, web_uri text not null, uid text not null, keypath text not null, ts int not null, statistics text, isUploaded int default 0, unique(uid, md5, keypath))")
        self.conn.execute("create index if not exists web_uri on t_videos (web_uri)")
        self.conn.execute("create index if not exists md5 on t_videos (md5)")
        self.conn.execute("create table if not exists t_videos_xmly (id integer primary key autoincrement, md5 text not null, web_uri text not null, uid text not null, statistics text, isUploaded int default 0, unique(uid, md5))")
        self.conn.execute("create index if not exists keypath on t_videos (keypath)")
        self.conn.execute("create table if not exists t_videos_failed (id integer primary key autoincrement, url text unique not null, web_uri text not null, uid text not null, ts int not null, statistics text)")
        self.conn.execute("create table if not exists t_user_avatars (id integer primary key autoincrement, uid text not null, md5 text not null, ts int not null, unique(uid, md5))")
        self.conn.execute("create table if not exists t_catagory (id integer primary key autoincrement, source_id text not null unique, title text not null, desc text not null, view_count int, user_count int)")
        self.conn.commit()
    def __del__(self):
        logging.debug('%s begin', __class__)
        self.conn.close()
    
    def insertUser(self, para):
        logging.debug('%s begin', __class__)
        sql = '''insert or replace into t_users (short_id, uid, nickname, gender, location, mplatform_followers_count, follower_count, aweme_count , total_favorited) values (?,?,?,?,?,?,?,?,?)'''
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
        sql = '''insert or ignore into t_videos (md5, web_uri, uid, keypath, ts, statistics) values (?,?,?,?,?,?)'''
        self.conn.execute(sql_del, (para[1],))
        self.conn.execute(sql, para)
        self.conn.commit()
    def insertVideo_xmly(self, para):
        logging.debug('%s begin', __class__)
        sql = '''insert or ignore into t_videos_xmly (md5, web_uri, uid, statistics) values (?,?,?,?)'''
        self.conn.execute(sql, para)
        self.conn.commit()
    def insertCatagory(self, para):
        logging.debug('%s begin', __class__)
        sql = '''insert or replace into t_catagory (source_id, title, desc, view_count, user_count) values (?,?,?,?,?)'''
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
    def isVideoExist_xmly(self, para) -> bool:
        logging.debug('%s begin', __class__)
        sql = '''select web_uri from t_videos_xmly where web_uri = ?'''
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
        def desc(self):
            return 'no desc'
    class Sound_xmly(Source):
        def __init__(self, url, web_uri, uid, statistics):
            logging.debug('%s begin', __class__)
            self.url = url
            self.web_uri = web_uri
            self.uid = uid
            self.statistics = statistics
        def run(self):
            if Singleton_sql.get_instance().isVideoExist_xmly((self.web_uri,)):
                logging.info('%s video is exist, web_uri: %s', __class__, self.web_uri)
                pass
            else:
                try:
                    s = requests.Session()
                    s.mount('http://', HTTPAdapter(max_retries=5))
                    s.mount('https://', HTTPAdapter(max_retries=5))
                    res = s.get(self.url, stream = True, timeout=5)
                    md5 = hashlib.md5()
                    md5.update(res.content)
                    filename = md5.hexdigest() + '.mp3'
                    dir_path = '/Volumes/data/xmly_video/' + self.uid
                    isExists = os.path.exists(dir_path)
                    if not isExists:
                        os.makedirs(dir_path)
                    path = dir_path + '/' + filename
                    with open(path,  'wb') as f:
                        f.write(res.content)
                        f.flush()
                    param = (md5.hexdigest(), self.web_uri, self.uid, self.statistics)
                    logging.info(param.__str__())
                    Singleton_sql.get_instance().insertVideo_xmly(param)
                except:
                    #logging.warning('download video failure:%s, statistics: %s', self.url, self.statistics)
                    logging.error('video list info error: %s', traceback.format_exc())
    class Video(Source):
        def __init__(self, url, web_uri, uid, ts, statistics, keypath, if_ge: int):
            logging.debug('%s begin', __class__)
            self.url = url
            self.web_uri = web_uri
            self.keypath = keypath
            self.uid = uid
            self.ts = ts
            self.statistics = statistics
            self.if_ge = if_ge
        def run(self):
            logging.debug('%s begin', __class__)
            #follower_count = Singleton_sql.get_instance().queryUser_follower(self.uid)
            #logging.info('if_ge %d, followercount %d', self.if_ge, follower_count)
            #if follower_count < self.if_ge:
            #    return
            if Singleton_sql.get_instance().isVideoExist((self.web_uri,)):
                logging.info('%s video is exist, web_uri: %s', __class__, self.web_uri)
                pass
            else:
                try:
                    #res = requests.get(self.url, stream = True, timeout = 5)
                    proxies = {
                                "http": "http://127.0.0.1:8888",
                                "https": "http://127.0.0.1:8888",
                                }
                    s = requests.Session()
                    s.mount('http://', HTTPAdapter(max_retries=5))
                    s.mount('https://', HTTPAdapter(max_retries=5))
                    headers = {'User-Agent': 'com.ss.android.ugc.aweme/340 (Linux; U; Android 8.1.0; zh_CN; ZTE V0900; Build/OPM1.171019.026; Cronet/58.0.2991.0)'}
                    #res_first = s.get(self.url, stream = True, timeout=5)
                    res = s.get(self.url, stream = True, timeout=5, headers = headers)
                    logging.info("requests headers: %s", res.headers)

                    #bs = BeautifulSoup(res_first.text, "lxml")
                    #bsl = bs.find('a')
                    #res  = None
                    #if bsl == None:
                    #    res = res_first
                    #else:
                    #    s = requests.Session()
                    #    s.mount('http://', HTTPAdapter(max_retries=5))
                    #    s.mount('https://', HTTPAdapter(max_retries=5))
                    #    self.url = bsl.get('href')
                    #    res = s.get(self.url, stream = True, timeout=5)
                    md5 = hashlib.md5()
                    md5.update(res.content)
                    filename = md5.hexdigest() + '.mp4'
                    path = '/Volumes/data/video/' + filename
                    with open(path,  'wb') as f:
                        f.write(res.content)
                        f.flush()
                    param = (md5.hexdigest(), self.web_uri, self.uid, self.keypath, self.ts, self.statistics)
                    logging.info(param.__str__())
                    Singleton_sql.get_instance().insertVideo(param)
                except:
                    logging.warning('download video failure:%s', self.url)
                    Singleton_sql.get_instance().insertVideoFailed((self.url, self.web_uri, self.uid, self.ts, self.statistics))
        def desc(self):
            return 'video:' + self.url + self.keypath
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
    class Category(Source):
        def __init__(self, source_id:str, title: str, desc: str, view_count: int, user_count: int):
            logging.debug('%s begin', __class__)
            self.source_id = source_id
            self.title = title
            self.desc_l = desc
            self.view_count = view_count
            self.user_count = user_count
        def run(self):
            logging.debug('%s begin', __class__)
            Singleton_sql.get_instance().insertCatagory((self.source_id, self.title, self.desc_l, self.view_count, self.user_count))
        def desc(self):
            return self.source_id + ":" + self.title + ":" + self.desc_l


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

class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient(host=['mongodb://localhost:27017/'])
        self.db = self.client['toutiao-db']
        self.user_video_infos = self.db['user.video.infos']
        self.user_video_infos.create_index([('video_id', pymongo.ASCENDING)], unique = True)
        self.video_path = '/Volumes/data/toutiao/'
        isExists = os.path.exists(self.video_path)
        if not isExists:
            os.makedirs(self.video_path)
        self.up_path = '/Users/yijian/Desktop/tvideo'
        with open('toutiao_bunyun.json', 'r') as f:
            self.user_infos = json.load(f)
    def video_info_upsert_one(self, info:dict):
        re = self.user_video_infos.update_one({'video_id': info["video_id"]}, { '$set': info}, upsert=True)
        logging.info("matched_cout: {}, modified_count: {}".format(re.matched_count, re.modified_count))

class Singleton_Mongo:
    instance = None
    @staticmethod
    def get_instance():
        if Singleton_Mongo.instance is None:
            Singleton_Mongo.instance = Mongo()
        return Singleton_Mongo.instance

class UserInfoer:
    
        
    def load(self, entry: addonmanager.Loader):
        ctx.log.alert('load begin')
        logging.getLogger('').handlers = []
        log_format = "[%(asctime)s:%(levelname)s:%(thread)d:%(filename)s:%(lineno)d:%(funcName)s]%(message)s"
        logging.basicConfig(filename='1m.log', level=logging.ERROR, format=log_format)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("wsgi").setLevel(logging.WARNING)
        logging.debug('%s log init test', __class__)
        
    #def requestheaders(self, flow: http.HTTPFlow):
    #    flow.request.stream = True
    #def responseheaders(self, flow: http.HTTPFlow):
    #    flow.response.stream = True
                
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
                user_info = (user['short_id'], user['uid'], user['nickname'], user['gender'], user['location'], user['mplatform_followers_count'], user['follower_count'], user['aweme_count'], user['total_favorited'])
                u_task = DownloadThread.Userinfo(user_info)
                Singleton_tread.get_instance().addTasks([u_task], True)
                # insert avatar
                avatar_url = user['avatar_larger']['url_list'][0]
                a_task = DownloadThread.Avatar(avatar_url, user['uid'])
                Singleton_tread.get_instance().addTasks([a_task])
            except:
                logging.error('user info error: %s', traceback.format_exc())
        if (flow.request.url.find('/aweme/v1/aweme/post/') != -1 or
            flow.request.url.find('/aweme/v1/search/item/') != -1):
            try:
                logging.info('user produce url %s',flow.request.url)
                res_dict = json.loads(flow.response.get_text())
                #fields = flow.request.query.fields
                #for tt in enumerate(fields):
                #    if tt[1][0] == 'user_id':
                #        self.uid = tt[1][1]
                #    elif tt[1][0] == 'ts':
                #        self.ts = tt[1][1]
                video_list = res_dict['aweme_list']
                videos = []
                for video in enumerate(video_list):
                    try:
                        url = video[1]['video']['play_addr']['url_list'][0]
                        uri = video[1]['video']['play_addr']['uri']
                        uid = video[1]['author_user_id']
                        ts = video[1]['create_time']
                        statistics = video[1]['statistics']
                        title = video[1]['share_info']['share_title']
                        statistics['share_title'] = title
                        keypath = 'userlist'
                        if flow.request.url.find('/search/') != -1:
                            keypath = 'search'
                            fields = flow.request.query.fields
                            for tt in enumerate(fields):
                                if tt[1][0] == 'keyword':
                                    keypath += '.' + tt[1][1]
                        #v = DownloadThread.Video(url, uri, self.uid, self.ts, json.dumps(statistics), json.dumps(video[1]), 94000)
                        v = DownloadThread.Video(url, uri, uid, ts, json.dumps(statistics), keypath, 94000)
                        videos.append(v)
                    except:
                        logging.error('video info error: %s', traceback.format_exc())
                        continue
                Singleton_tread.get_instance().addTasks(videos)
            except:
                logging.error('video list info error: %s', traceback.format_exc())

        if flow.request.url.find('/aweme/v1/category/list/') != -1:
            try:
                logging.info('user produce url %s',flow.request.url)
                res_dict = json.loads(flow.response.get_text())
                category_list = res_dict['category_list']
                categorys = []
                for cate in enumerate(category_list):
                    try:
                        title = ''
                        desc = cate[1]['desc']
                        view_count = 0
                        user_count = 0
                        source_id = ''
                        if 'challenge_info' in cate[1]:
                            title = cate[1]['challenge_info']['cha_name']
                            view_count = cate[1]['challenge_info']['view_count']
                            user_count = cate[1]['challenge_info']['user_count']
                            source_id = cate[1]['challenge_info']['cid']
                        elif 'music_info' in cate[1]:
                            title = cate[1]['music_info']['title']
                            user_count = cate[1]['music_info']['user_count']
                            source_id = cate[1]['music_info']['id_str']
                        else:
                            logging.error('no key in catagory list')
                        c = DownloadThread.Category(source_id, title, desc, view_count, user_count)
                        categorys.append(c)
                    except:
                        logging.error('category info error: %s', traceback.format_exc())
                        continue
                Singleton_tread.get_instance().addTasks(categorys)
            except:
                logging.error('video list info error: %s', traceback.format_exc())

        if flow.request.url.find('/mobile/v1/album/track/') != -1:
            try:
                logging.info('xmly produce url %s',flow.request.url)
                res_dict = json.loads(flow.response.get_text())
                data_list = res_dict['data']['list']
                datas = []
                for item_t in enumerate(data_list):
                    item = item_t[1]
                    title = item['title']
                    uid = str(item['uid'])
                    url = item['playUrl64']
                    order_no = item['orderNo']
                    web_uri = str(item['trackId']) + ":" + uid
                    statistics = dict()
                    statistics['title'] = title
                    statistics['order_no'] = order_no
                    c = DownloadThread.Sound_xmly(url, web_uri, uid, json.dumps(statistics))
                    datas.append(c)
                Singleton_tread.get_instance().addTasks(datas)
            except:
                logging.error('video list info error: %s', traceback.format_exc())
        
        # toutiao
        if flow.request.url.find('api/feed/profile/v1/?category=profile_video&visited_uid=') != -1:
            try:
                logging.info('toutiao url %s', flow.request.url)
                filled_line = re.sub(r'\\\\\\"', '"', flow.response.get_text())
                filled_line = re.sub(r'\\"', '"', filled_line)
                filled_line = re.sub(r'"{', '{', filled_line)
                filled_line = re.sub(r'}"', '}', filled_line)
                data = json.loads(filled_line)
                for item_t in enumerate(data["data"]):
                    content = item_t[1]["content"]
                    video_info = dict()
                    video_info["item_id"] = content["item_id"]
                    t = video_info["publish_time"] = content["publish_time"]
                    d = datetime.datetime.fromtimestamp(t)
                    video_info["year"] = d.strftime("%Y")
                    video_info["month"] = d.strftime("%m")
                    video_info["day"] = d.strftime("%d")
                    video_info["hour"] = d.strftime("%H:%M:%S")
                    video_info["req_id"] = content["req_id"]
                    video_info["share_url"] = content["share_url"]
                    video_info["source"] = content["source"]
                    video_info["video_id"] = content["video_id"]
                    video_info["video_duration"] = content["video_duration"]
                    video_info["title"] = content["title"]
                    video_info["video_watch_count"] = content["video_detail_info"]["video_watch_count"]
                    Singleton_Mongo.get_instance().video_info_upsert_one(video_info)

            except:
                logging.error('tt video list info error: %s', traceback.format_exc())

    #def request(self, flow: http.HTTPFlow):
    #    if flow.request.url.find('/video/m/') != -1:
    #        logging.info('in url %s',flow.request.url)
    #        url = "http://" + flow.request.host_header + flow.request.path
    #        logging.info('in url %s',url)
    #        try:
    #            with open("t-video-url.txt", 'a+') as f:
    #                f.write(url+'\n')
    #        except:
    #            logging.error('video list info error: %s', traceback.format_exc())


addons = [
    UserInfoer()
]