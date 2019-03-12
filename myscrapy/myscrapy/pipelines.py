# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from mydb.mydb import database
import time
class MyscrapyPipeline(object):
    def process_item(self, item, spider):
        return item

class SqlitePipeline(object):
    def __init__(self):
        self.db = database()


    def open_spider(self,spider):##在一开启爬虫的时候调用
        time.clock()
        self.db._createdb()
        self.db.connect()##创建并连接数据库
        print("!!database is connected")

    def close_spider(self,spider):##在关闭爬虫的时候调用
        self.db.disconnect()##与数据库断开连接
        print("!!database disconnected")

    def process_item(self, item, spider):##在爬虫返回爬取的item数据之后
        data = item["data"]
        for datalist in data:
            self.db.insert(datalist)##将数据插入数据库
        print("insert an item in database")
        return None





