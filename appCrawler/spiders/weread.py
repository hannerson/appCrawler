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
    name = 'weread'
    allowed_domains = ['weread.qq.com']
    start_urls = []
    custom_settings = {
        'ITEM_PIPELINES':{'appCrawler.pipelines.MysqlUpdatePipeline':300}
    }

    def start_requests(self):
        headers = {
            "accept-language": "zh-CN,zh;q=0.9",
            "Referer": "https://weread.qq.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            "Accept": "application/json, text/javascript, */*",
            "accept-encoding": "gzip, deflate, br",
            "cookie": "pgv_pvid=2466533848; pgv_pvi=4576642048; RK=+DQl9ZXSOo; ptcz=3b7f4fa72eb3ca1f4a08995b00b6f2f39ee2616b5c1367ab91e5edbde8b30b5d; wr_gid=245357230; psrf_qqunionid=; psrf_qqopenid=0FEB8002EE4DFE8AEAF66D1659E9102B; euin=NeEP7eclNe4s; psrf_access_token_expiresAt=1615365400; psrf_qqaccess_token=3B9DE6E72E1DB4E6AEDEA296E2C95595; uin=894487856; tmeLoginType=2; psrf_qqrefresh_token=0E0BE57A74A88BB670AA24CD69A83ED8; o_cookie=894487856; pac_uid=1_94487856; wr_localvid=; wr_name=; wr_avatar=; wr_gender=; tvfe_boss_uuid=8cf9d7565a55657d",
        }

        session = scoped_session(SQLSession)
        urls = []
        results = session.query(cpmKeywords.id,cpmKeywords.keyword,cpmKeywords.creator).all()
        url_pattern = "https://weread.qq.com/web/search/global?keyword=%s&maxIdx=0&fragmentSize=120&count=10"
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
        if response.status != 200:
            return
        if "books" not in results:
            return
        for ret in results["books"]:
            extra = response.meta["extra"]
            albumid = ret["bookInfo"]["bookId"]
            albumpic = ret["bookInfo"]["cover"]
            albumname = ret["bookInfo"]["title"]
            singer = ret["bookInfo"]["author"]
            extra["source_id"] = albumid
            extra["name"] = albumname
            extra["artist"] = singer
            extra["finished"] = ret["bookInfo"]["finished"]
            if "star" in ret["bookInfo"]:
                extra["fav_num"] = ret["bookInfo"]["star"]
            extra["intro"] = ret["bookInfo"]["intro"].replace("\t"," ").replace("\r\n","").replace("\n","")
            self.log("process albumid %s" % (albumid), level=logging.INFO)

            item = searchItem()
            for k,v in extra.items():
                item[k] = v
            item["created_at"] = "%s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            item["cdate"] = "%s" % (datetime.datetime.now().strftime('%Y-%m-01'))
            yield item
            #break
            pass
