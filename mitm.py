from bs4 import BeautifulSoup
from mitmproxy import ctx, http
import hashlib
import requests
import sqlite3
import json
import time

class Sql_dy:
    conn = None
    def __init__(self):
        raise SyntaxError('can not instance, please use get_instance')
    def __del__(self):
        Sql_dy.conn.close()
    
    def insertUser(self, para):
        sql = '''insert or replace into t_users (short_id, uid, nickname, gender, location, following_count, follower_count, aweme_count , total_favorited) values (?,?,?,?,?,?,?,?,?)'''
        self.conn.execute(sql, para)
        self.conn.commit()
    def insertVideo(self, para):
        sql = '''insert or ignore into t_videos (md5, uid, ts) values (?,?,?)'''
        self.conn.execute(sql, para)
        self.conn.commit()
    def insertAvatars(self, para):
        sql = '''insert or ignore into t_user_avatars (md5, uid, ts) values(?,?,?)'''
        self.conn.execute(sql, para)
        self.conn.commit()
class Singleton_sql(Sql_dy):
    instance = None
    @staticmethod
    def get_instance():
        if Singleton_sql.instance is None:
            Singleton_sql.instance = Sql_dy.__new__(Sql_dy)
            Singleton_sql.instance.conn = sqlite3.connect('dy.db')
            Singleton_sql.instance.conn.execute("create table if not exists t_users (id integer primary key autoincrement, short_id text not null, uid text unique not null, nickname text, gender int not null, location text, following_count int not null, follower_count int not null, aweme_count int not null, total_favorited int not null)")
            Singleton_sql.instance.conn.execute("create index if not exists uid on t_users (uid)")
            Singleton_sql.instance.conn.execute("create index if not exists short_id on t_users (short_id)")
            Singleton_sql.instance.conn.execute("create index if not exists follower_count on t_users (follower_count)")
            Singleton_sql.instance.conn.execute("create index if not exists aweme_count on t_users (aweme_count)")
            Singleton_sql.instance.conn.execute("create table if not exists t_videos (id integer primary key autoincrement, md5 text unique not null, uid text not null, ts int not null, unique(uid, md5))")
            Singleton_sql.instance.conn.execute("create table if not exists t_user_avatars (id integer primary key autoincrement, uid text not null, md5 text not null, ts int not null, unique(uid, md5))")
            Singleton_sql.instance.conn.commit()
        return Singleton_sql.instance

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
    def response(self, flow: http.HTTPFlow) -> None:
        #ctx.log.info('userinfo runing -------------------------------')
        #ctx.log.info(flow.request.url)
        if flow.request.url.startswith('https://aweme-eagle.snssdk.com/aweme/v1/user'):
            user_res = requests.get(flow.request.url, stream = True)
            data = user_res.json()
            user = data['user']
            user_info = (user['short_id'], user['uid'], user['nickname'], user['gender'], user['location'], user['following_count'], user['follower_count'], user['aweme_count'], user['total_favorited'])
            ctx.log.info(user_info.__str__())
            Singleton_sql.get_instance().insertUser(user_info)
            avatar_url = user['avatar_larger']['url_list'][0]
            avatar_res = requests.get(avatar_url, stream = True)
            md5 = hashlib.md5()
            md5.update(avatar_res.content)
            path = '/Volumes/data/avatar/' + md5.hexdigest() + '.jpeg'
            with open(path, 'ab') as f:
                f.write(avatar_res.content)
                f.flush()
            avatar_t = (md5.hexdigest(), user['uid'], int(time.time()))
            ctx.log.info(avatar_t.__str__())
            Singleton_sql.get_instance().insertAvatars(avatar_t)
        if flow.request.url.find('/aweme/v1/aweme/post/') != -1:
            #ctx.log.info('-------------------------------')
            #ctx.log.info(flow.request.query.fields.__str__())
            ctx.log.info(flow.request.url)
            res_dict = json.loads(flow.response.get_text())
            #ctx.log.info(flow.request.url)
            fields = flow.request.query.fields
            uid = ""
            ts = ""
            for tt in enumerate(fields):
                if tt[0] == 'user_id':
                    uid = tt[1]
                elif tt[0] == 'ts':
                    ts = tt[1]
            video_list = res_dict['aweme_list']
            for video in enumerate(video_list):
                url = video[1]['video']['play_addr']['url_list'][0]
                ctx.log.info(url)
                res = requests.get(url, stream = True)
                md5 = hashlib.md5()
                md5.update(res.content)
                filename = md5.hexdigest() + '.mp4'
                path = '/Volumes/data/video/' + filename
                #ctx.log.info(path)
                with open(path,  'ab') as f:
                    f.write(res.content)
                    f.flush()
                ctx.log.info(path)
                param = (md5.hexdigest(), uid, ts)
                ctx.log.info(param.__str__())
                Singleton_sql.get_instance().insertVideo(param)





addons = [
    UserInfoer(),
    TrackRecorder()
]