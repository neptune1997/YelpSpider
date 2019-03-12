import request_crawler
from mydb import database
import time
import requests


if __name__=='__main__':
    rc = request_crawler.req_crawler()
    time.clock()#启动计时
    rc.handle_single()##启动单线程模式进行爬取
    db = database()
    number = db.count
    print("the request crawler finished\n get total data number: {}\ntotal time:{} \n".format(number, time.clock()))