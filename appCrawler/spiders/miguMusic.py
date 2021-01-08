import scrapy
import json
import time
import datetime
import sys
from modelsql import *
import urllib.parse
from appCrawler.items import searchItem
import logging


class MigumusicSpider(scrapy.Spider):
    name = 'miguMusic'
    allowed_domains = ['migu.cn']
    start_urls = ['https://app.c.nf.migu.cn/MIGUM3.0/bmw/page-data/index-show/v1.0?templateVersion=1']
    custom_settings = {
        'ITEM_PIPELINES':{'appCrawler.pipelines.MysqlUpdatePipeline':300}
    }

    def start_requests(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            #"accept-encoding": "",
            "accept-language": "zh-CN,zh;q=0.9",
            #"cookie": "Hm_lvt_ec5a5474d9d871cb3d82b846d861979d=1608797648; migu_cookie_id=55229cb8-6871-4e33-8554-812ef86a9497-n41609845927857; WT_FPC=id=24d25868eb8485b94f91608797645758:lv=1609846093936:ss=1609845928888",
            #"referer": "https://music.migu.cn/v3/search?page=1&type=song&i=f704a89cedb7d7227e0a4f5c76b9a5187fa86b71&f=html&s=1609846092&c=001002A&keyword=%E5%BF%AB%E4%B9%90&v=3.13.4",
            "Referer": "https://m.music.migu.cn/migu/l/?s=149&p=163&c=5111&j=l&keyword=%E9%9D%92%E8%8A%B1%E7%93%B7",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

        session = scoped_session(SQLSession)
        urls = []
        results = session.query(cpmKeywords.id,cpmKeywords.keyword,cpmKeywords.creator).all()
        url_pattern = "https://m.music.migu.cn/migu/remoting/scr_search_tag?rows=20&type=4&keyword=%s&pgc=1"
        for ret in results:
            extra = {}
            extra["keyword_id"] = "%s" % (ret[0])
            extra["keyword"] = "%s" % (ret[1])
            extra["creator"] = "%s" % (ret[2])
 
            #r = "青花瓷"
            url = url_pattern % (urllib.parse.quote(ret[1]))
            #url = url_pattern % (urllib.parse.quote(r))
            self.log("search : %s" % (url), level=logging.INFO)
            req = scrapy.Request(url=url, headers=headers, callback=self.parse_search)
            req.meta["extra"] = extra
            yield req
            #break
            time.sleep(1)
        session.remove()

    def parse_search(self, response):
        self.log("parse search", level=logging.INFO)
        results = json.loads(response.body.decode("utf-8"))
        #print (results)
        if "albums" not in results:
            return
        headers = {
            "deviceId": "3071C179ED9059775C780799873AC833",
            #"sign": "6c79a99f1caca363dace89bf449ea06e",
            "sign": "98159ceb9dc1da6e52c5a1dd9b541576",
            #"mgm-Network-type": "04",
            #"IMSI": "460007171722277",
            #"HWID": "",
            #"mac": "02:27:e9:8b:b3:c0",
            #"timestamp": "1608802245457",
            "timestamp": "1608802365531",
            #"appId": "yyapp2",
            #"mgm-Network-standard": "01",
            #"os": "android 7.1.2",
            #"platform": "HD1910",
            #"IMEI": "864267189642846",
            #"mode": "android",
            #"brand": "OnePlus",
            #"OAID": "",
            #"ua": "Android_migu",
            "version": "7.0.7",
            #"osVersion": "android 7.1.2",
            #"ip": "10.0.2.15",
            "uiVersion": "A_music_3.4.0",
            #"uid": "",
            #"msisdn": "",
            #"channel": "0146971",
            #"android_id": "2be2bf49fa4560a2",
            #"Host": "jadeite.migu.cn",
            #"Connection": "Keep-Alive",
            #"Accept-Encoding": "gzip",
            #"User-Agent": "okhttp/3.12.12",
        }
        for ret in results["albums"]:
            extra = response.meta["extra"]
            albumid = ret["id"]
            albumpic = ret["albumPicS"]
            albumname = ret["title"]
            singer = ""
            for r in ret["singer"]:
                singer += r["name"] + "###"
            singer = singer.strip("###")
            extra["source_id"] = albumid
            #extra["albumpic"] = albumpic
            extra["name"] = albumname
            extra["artist"] = singer
            self.log("process albumid %s" % (albumid), level=logging.INFO)
            url = "https://app.c.nf.migu.cn/MIGUM2.0/v1.0/content/getAlbumDescribe?albumId=%s" % (albumid)
            req = scrapy.Request(url=url, headers=headers, callback=self.parse_item)
            req.meta["extra"] = extra
            yield req
            time.sleep(1)
            #break
        pass

    def parse_item(self, response):
        #print (response.status, response.body.decode("utf-8"))
        results = json.loads(response.body.decode("utf-8"))
        #print (results)
        if results["code"] != "000000":
            return
        headers = {
            "deviceId": "3071C179ED9059775C780799873AC833",
            #"sign": "6c79a99f1caca363dace89bf449ea06e",
            "sign": "98159ceb9dc1da6e52c5a1dd9b541576",
            #"mgm-Network-type": "04",
            #"IMSI": "460007171722277",
            #"HWID": "",
            #"mac": "02:27:e9:8b:b3:c0",
            #"timestamp": "1608802245457",
            "timestamp": "1608802365531",
            #"appId": "yyapp2",
            #"mgm-Network-standard": "01",
            #"os": "android 7.1.2",
            #"platform": "HD1910",
            #"IMEI": "864267189642846",
            #"mode": "android",
            #"brand": "OnePlus",
            #"OAID": "",
            #"ua": "Android_migu",
            "version": "7.0.7",
            #"osVersion": "android 7.1.2",
            #"ip": "10.0.2.15",
            "uiVersion": "A_music_3.4.0",
            #"uid": "",
            #"msisdn": "",
            #"channel": "0146971",
            #"android_id": "2be2bf49fa4560a2",
            #"Host": "jadeite.migu.cn",
            #"Connection": "Keep-Alive",
            #"Accept-Encoding": "gzip",
            #"User-Agent": "okhttp/3.12.12",
        }
        extra = response.meta["extra"]
        if "summary" in results["data"]:
            extra["intro"] = results["data"]["summary"].replace("\t"," ").replace("\r\n","").replace("\n","")
        albumid = extra["source_id"]
        url = "https://app.c.nf.migu.cn/MIGUM3.0/v1.0/content/queryOPNumItemsAction.do?id=%s&resourceType=2021" % (albumid)
        req = scrapy.Request(url=url, headers=headers, callback=self.parse)
        req.meta["extra"] = extra
        yield req
        pass

    def parse(self, response):
        #print (response.status, response.body.decode("utf-8"))
        results = json.loads(response.body.decode("utf-8"))
        #print (results)
        if results["code"] != "000000":
            return
        extra = response.meta["extra"]
        item = searchItem()
        for k,v in extra.items():
            item[k] = v
        item["play_num"] = results["userOpNums"][0]["opNumItem"]["playNum"]
        item["sub_num"] = results["userOpNums"][0]["opNumItem"]["subscribeNum"]
        item["created_at"] = "%s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        yield item
        pass
