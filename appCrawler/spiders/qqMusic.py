import scrapy
import json
import time
import datetime
import sys
from modelsql import *
import urllib.parse
from appCrawler.items import searchItem
import logging
import traceback


class QQMusicSpider(scrapy.Spider):
    name = 'qqMusic'
    allowed_domains = ['qq.com']
    start_urls = []
    custom_settings = {
        'ITEM_PIPELINES':{'appCrawler.pipelines.MysqlUpdatePipeline':300}
    }

    def start_requests(self):
        headers = {
            "accept-language": "zh-CN,zh;q=0.9",
            "Referer": "http://y.qq.com/musicmac/v3/search.html?key=%s&column=&subject=&nrnd=505281502&rnd=80245",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

        session = scoped_session(SQLSession)
        urls = []
        results = session.query(cpmKeywords.id,cpmKeywords.keyword,cpmKeywords.creator).all()
        pn = 1
        rn = 10
	    ###search for album tab
        url_pattern = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&remoteplace=txt.yqq.center&searchid=38066741890901674&aggr=0&catZhida=1&lossless=0&sem=10&t=8&w=%s&g_tk_new_20200303=1712602240&g_tk=1712602240&loginUin=894487856&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0" + "&p=%s&n=%s" % (pn, rn)
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
            break
            time.sleep(1)
        session.remove()

    def parse_search(self, response):
        self.log("parse search", level=logging.INFO)
        results = json.loads(response.body.decode("utf-8"))
        #print (results)
        if "data" not in results:
            return
        headers = {
            "accept-language": "zh-CN,zh;q=0.9",
            #"Referer": "http://y.qq.com/musicmac/v3/search.html?key=%s&column=&subject=&nrnd=505281502&rnd=80245",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }
        for ret in results["data"]["album"]["list"]:
            extra = response.meta["extra"]
            albumid = ret["albumID"]
            albumpic = ret["albumPic"]
            albumname = ret["albumName"]
            singer = ""
            for r in ret["singer_list"]:
                singer += r["name"] + "###"
            singer = singer.strip("###")
            extra["source_id"] = albumid
            #extra["albumpic"] = albumpic
            extra["name"] = albumname
            extra["artist"] = singer
            self.log("process albumid %s" % (albumid), level=logging.INFO)
            url = "http://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?format=json&albumid=%s" % (albumid)
            req = scrapy.Request(url=url, headers=headers, callback=self.parse)
            req.meta["extra"] = extra
            yield req
            time.sleep(1)
            #break
        pass

    def check_qq_pay(self,songlist):
        paydesc = {0:"free",1:"album",2:"song"}
        paydesc = {0:0,1:1,2:1}
        try:
            paytype = 0
            for info in songlist:
                if "pay" in info:
                    if info["pay"]["payalbum"] == 1:
                        paytype = 1
                        break
                    elif info["pay"]["payplay"] == 1:
                        paytype = 2
                        break
                return paydesc[paytype]
        except Exception as e:
            traceback.print_exc()
            return paydesc[0]

    def parse(self, response):
        #print (response.status, response.body.decode("utf-8"))
        results = json.loads(response.body.decode("utf-8"))
        #print (results)
        if results["code"] != 0:
            return
        extra = response.meta["extra"]
        item = searchItem()
        for k,v in extra.items():
            item[k] = v
        item["intro"] = results["data"]["desc"].replace("\t"," ").replace("\r\n","").replace("\n","")
        item["fee_type"] = self.check_qq_pay(results["data"]["list"])
        item["created_at"] = "%s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        yield item
        pass
