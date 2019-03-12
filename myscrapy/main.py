from scrapy.cmdline import execute
import sys
import os
from mydb.mydb import database
import time
if __name__=="__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    print(os.path.dirname(os.path.abspath(__file__)))
    execute(['scrapy', 'crawl', 'YelpSpider']) ##进入主函数
    db = database()
    db.connect()
    print("get {} restaurants in {}s".format(db.count,time.clock()))