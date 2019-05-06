import multiprocessing
import json
import pymongo
import shutil
import requests
import urllib3
import hashlib
import os
import subprocess
import ffmpeg
import time
import json
import re
import thulac
import traceback

class Data:
    def remove_extra_symbol(self, file_path):
        ex_file = ""
        with open(file_path, 'r') as f:
            for line in f:
                filled_line = re.sub(r'\\\\\\"', '"', line)
                filled_line = re.sub(r'\\"', '"', filled_line)
                filled_line = re.sub(r'"{', '{', filled_line)
                filled_line = re.sub(r'}"', '}', filled_line)
                ex_file += filled_line
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(ex_file)


class Reverse:
    def add_r_files(self, apk, r_dir_path):
        sub = 'aapt a ' + apk 
        for dirpath, _, files in os.walk(r_dir_path):
            for file in files:
                filepath = os.path.join(dirpath, file)
                #print("root:{}, file:{}, needed access permission".format(dirpath,file))
                sub += ' ' + filepath
                #print("filepath:{}.".format(filepath))
        subprocess.check_call(args = sub, shell=True)
        print("count:{}.".format(len(sub)))
    def insert_debug_log_root_dir(self, rootDir):
        if not os.path.isabs(rootDir):
            rootDir = os.path.abspath(rootDir)
            print("root dir: {}".format(rootDir))
        for dirpath, _, files in os.walk(rootDir):
            for file in files:
                filepath = os.path.join(dirpath,file)
                if os.access(filepath, os.F_OK | os.R_OK | os.W_OK) == True:
                    self.insert_debug_log(filepath)
                else: 
                    print("file:{}, needed access permission".format(filepath))
    def insert_debug_log(self, filepath):
        if not os.path.isabs(filepath):
            filepath = os.path.abspath(filepath)
        _, filename = os.path.split(filepath)
        _, ext = os.path.splitext(filename)
        if ".smali" == ext:
            #print("filename: {}, ext: {}".format(filename, ext))
            file_data = ""
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    file_data += line
                    # 
                    if re.search(r'\.class public Lcom/bytedance/common/utility/Logger;', line) != None:
                        print("{}: this file is logger, need not to insert logs.".format(filepath))
                        return
                    if re.search(r'\.locals', line) != None:
                        #print(line)
                        file_data += '\n    '
                        file_data += 'invoke-static {}, Lcom/bytedance/common/utility/Logger;->cLogDebug()V'
                        file_data += '\n'
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(file_data)

        else:
            #print("{}: is not smali file.".format(filename))
            pass

class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['toutiao-db']
        self.user_video_infos = self.db['user.video.infos']
        self.user_video_urls = self.db['user.video.urls']
        self.user_video_stop = self.db['user.video.stop']
    def findNeedDownloadVideos(self):
        return self.user_video_infos.aggregate([{"$match": {"upload_status": {"$exists": False}}},{"$lookup": { "from": "user.video.urls", "let": { "info_video_id": "$video_id"}, "pipeline": [ { "$match": {"$expr": { "$eq": ["$$info_video_id", "$video_id"]} } } ], "as": "video_urls" }}, {"$match": {"$expr": {"$ne": [{"$size":"$video_urls"}, 0] } } }, {"$replaceRoot": {"newRoot": {"video_id": "$video_id", "urlObj": {"$arrayElemAt": [ "$video_urls",0]} }}}, {"$replaceRoot": {"newRoot":{"video_id": "$video_id", "url": {"$arrayElemAt": [ "$urlObj.urls",0]}}}}, {"$limit": 100}])
    def downloadSuccess(self, video_id):
        self.user_video_infos.update_one({"video_id": video_id},{"$set": {"upload_status": "download success"}})
    def findNeedExtractVideos(self, name):
        return self.user_video_infos.find({"upload_status": "download success", "source": name}).sort("publish_time",pymongo.ASCENDING)
    def extractSuccess(self, video_id):
        self.user_video_infos.update_one({'video_id': video_id}, {'$set': {'upload_status': "extract success"}})
    def findNeedUploadVideos(self, name):
        return self.user_video_infos.find({"source": name, "upload_status": "extract success"}).sort("publish_time",pymongo.ASCENDING)
    def uploadSuccess(self, video_id):
        self.user_video_infos.update_one({"video_id": video_id},{"$set": {"upload_status": "upload success"}})
    def listen(self):
        while True:
            try:
                old_video_id = ""
                with self.user_video_urls.watch([{"$match": { "$or": [{'operationType': 'insert'}, {'operationType': 'replace'}]}}]) as steam:
                    for change in steam:
                        video_id = change['fullDocument']['video_id']
                        if video_id == old_video_id:
                            continue
                        else:
                            old_video_id = video_id
                            doc = self.user_video_infos.find_one({"video_id": video_id})
                            print(doc['source'])
                            if doc != None:
                                self.user_video_stop.update_one({"source": doc['source']},{"$inc": {"complete_count": 1}},True)
            except:
                print("listen except")

class MongoShared:
    instance = None
    @staticmethod
    def share():
        if MongoShared.instance is None:
            MongoShared.instance = Mongo()
        return MongoShared.instance

class Tool:

    class Download:
        def downloadVideos(self, video_path, item):
            #print("download pid: {}, item: {}".format(os.getpid(), item))
            #return {"isSuccess": False, "video_id": item["video_id"]}
            s = requests.Session()
            s.mount('http://', requests.adapters.HTTPAdapter(max_retries=5))
            s.mount('https://', requests.adapters.HTTPAdapter(max_retries=5))
            headers = {'User-Agent': 'com.ss.android.ugc.aweme/340 (Linux; U; Android 8.1.0; zh_CN; ZTE V0900; Build/OPM1.171019.026; Cronet/58.0.2991.0)'}
            res = s.get(item['url'], stream = True, timeout=5, headers = headers)
            if res.ok:
                filename = item['video_id']
                path = os.path.join(video_path, filename)
                with open(path,  'wb') as f:
                    f.write(res.content)
                    f.flush()
                    return {"isSuccess": True, "video_id": item["video_id"]}
            else:
                print("download error")
                return {"isSuccess": False, "video_id": item["video_id"]}
        def callback(self, item):
            print("callback pid: {}, item: {}".format(os.getpid(), item))
            if item["isSuccess"]:
                MongoShared.share().downloadSuccess(item["video_id"])
            
    def __init__(self):
        self.download = Tool.Download()
        self.video_path = '/Volumes/data/toutiao'
        isExists = os.path.exists(self.video_path)
        if not isExists:
            os.makedirs(self.video_path)
        self.up_path = '/Users/yijian/Desktop/tvideo'
        with open('toutiao_bunyun.json', 'r') as f:
            self.user_infos = json.load(f)
    def downloadVideos(self):
        items_contine_zero_count = 0
        isLoop = True
        while isLoop:
            try:
                items = MongoShared.share().findNeedDownloadVideos()
                if items.alive == False:
                    items_contine_zero_count += 1
                    if items_contine_zero_count >= 10:
                        break
                    time.sleep(1)
                    continue
                else:
                    items_contine_zero_count = 0
                for item in items:
                    s = requests.Session()
                    s.mount('http://', requests.adapters.HTTPAdapter(max_retries=5))
                    s.mount('https://', requests.adapters.HTTPAdapter(max_retries=5))
                    headers = {'User-Agent': 'com.ss.android.ugc.aweme/340 (Linux; U; Android 8.1.0; zh_CN; ZTE V0900; Build/OPM1.171019.026; Cronet/58.0.2991.0)'}
                    res = s.get(item['url'], stream = True, timeout=5, headers = headers)
                    if res.ok:
                        filename = item['video_id']
                        path = os.path.join(self.video_path, filename)
                        with open(path,  'wb') as f:
                            f.write(res.content)
                            f.flush()
                            MongoShared.share().downloadSuccess(item["video_id"])
                    else:
                        print("download error")

            except:
                isLoop = False
                print("download except")
    def downloadVideos_multi(self):
        isLoop = True
        while isLoop:
            try:
                items = MongoShared.share().findNeedDownloadVideos()
                if items.alive == False:
                    time.sleep(3)
                    continue
                pool = multiprocessing.Pool(processes=10)
                for item in items:
                    pool.apply_async(self.download.downloadVideos, (self.video_path, item), callback=self.download.callback)
                pool.close()
                pool.join()
            except :
                isLoop = False
                print("download multi error: {}".format(traceback.format_exc()))
    def logoXigua(self, vw: float, vh: float):
        h = 140.0 / 1460.0 * vh
        w = h * 500.0 / 140.0
        rp = h * 76.0 / 140.0
        tp = h * 78.0 / 140.0
        return (vw - w - rp, tp, w, h)
    def removeLogo(self, path, video_info):
        info = ffmpeg.probe(path)
        h = 0
        w = 0
        d_time = 0.0
        for s in info['streams']:
            if s['codec_type'] == 'video':
                w = s['width']
                h = s['height']
                d_time = float(s['duration'])
        stream = ffmpeg.input(path)
        sv = stream['v']
        sa = stream['a']
        logos = [self.logoXigua(w,h)]
        for lx, ly, lw , lh in logos:
            sv = ffmpeg.filter(sv, 'delogo', x=lx, y=ly, w=lw, h=lh)
        #joined = ffmpeg.concat(sv, sa).node
        outname = '{}.mp4'.format(int(time.time()))
        out = ffmpeg.output(sv, sa, outname, ss=video_info['start_trim'], to=d_time - video_info['end_trim'])
        out.run()
        return outname
    def extractVideos(self):
        for obj in self.user_infos.items():
            name = obj[0]
            if obj[1]['is_upload'] == True:
                self.extractVideoName(name)
    def extractVideoName(self, name):
        items = MongoShared.share().findNeedExtractVideos(name)
        for item in items:
            print(item)
            if item == None:
                break
            else:
                filepath = os.path.join(self.video_path, item["video_id"])
                outpath = self.removeLogo(filepath, self.user_infos[item['source']])
                shutil.move(outpath, os.path.join(self.up_path, item["video_id"] + ".mp4"))
                MongoShared.share().extractSuccess(item["video_id"])
    def uploadVideos(self):
        for obj in self.user_infos.items():
            name = obj[0]
            if obj[1]['is_upload'] == True:
                self.uploadVideoName(name)
    def uploadVideoName(self, name):
        infos = MongoShared.share().findNeedUploadVideos(name)
        for info in infos:
            file_path = os.path.join(self.up_path, info["video_id"] + ".mp4")
            if os.path.exists(file_path) == True:
                name = info['source']
                title = info['title']
                tags = ""
                t = thulac.thulac()
                tag_list = t.cut(title)
                for tag in tag_list:
                    if tag[1].startswith("n") or tag[1].startswith("s") or tag[1].startswith("v") or tag[1].startswith("x"):
                        tags = tags + tag[0] + ","
                user_info = self.user_infos[name]
                sub_client = "cp /Users/yijian/.youtube-upload-credentials.json.{} /Users/yijian/.youtube-upload-credentials.json".format(user_info['upload_c'])
                subprocess.check_call(args = sub_client, shell=True)
                sub = "proxychains4 /Users/yijian/Desktop/dy/youtube-upload-master/bin/youtube-upload --client-secrets=/Users/yijian/Desktop/dy/client_ms.json --title=\"" + title +  "\" --tags=\"" + tags + "\" " + file_path
                subprocess.check_call(args = sub, shell=True)
                MongoShared.share().uploadSuccess(info["video_id"])
                os.remove(file_path)
            else:
                print("not find file for video id: {}".format(info['video_id']))
    def listen(self):
        MongoShared.share().listen()

if __name__ == '__main__':
    print("main pid: {}".format(os.getpid()))
    t = Tool()
    t.downloadVideos_multi()
                


