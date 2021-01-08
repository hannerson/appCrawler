# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import signals
from modelsql import *
import logging


class DefaultPipeline:
    def process_item(self, item, spider):
        print (item)
        return item


class MysqlUpdatePipeline:
    def __init__(self):
        self.sql_session_pool = SQLSession
        self.session = scoped_session(SQLSession)
        self.spider_name = None

    def open_spider(self, spider):
        self.spider_name = spider.name
        spider.log("------spider start------", level=logging.INFO)
        pass

    def process_item(self, item, spider):
        #print ("-----------------")
        spider.log("process item: %s" % (item["source_id"]), level=logging.INFO)
        item["source_name"] = "%s" % (spider.name)
        sql_update = " ON DUPLICATE KEY UPDATE "
        sql_fields = ""
        sql_values = ""
        for k,v in item.items():
            sql_fields += "%s," % (k)
            sql_values += "\"%s\"," % (v)
            if k == "created_at":
                continue
            sql_update += "%s=\"%s\"," % (k, v)
        sql_update = sql_update.strip(",")
        sql_fields = sql_fields.strip(",")
        sql_values = sql_values.strip(",")
        sql = "insert into cpm_keywords_grab (%s) values (%s)" % (sql_fields,sql_values)+ sql_update
        spider.log(sql, level=logging.INFO)
        self.session.execute(sql)
        self.session.commit()
        pass

    def close_spider(self, spider):
        self.session.remove()
        spider.log("------spider close------", level=logging.INFO)
        pass

