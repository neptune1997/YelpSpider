from mydb import database
import requests
import threading
import sys
import queue
from ipproxy import ipproxy
from bs4 import BeautifulSoup
import time
from http import cookiejar
import numpy as np
from requests.packages.urllib3 import ProxyManager
from requests.exceptions import ProxyError
class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class custom_requests(object):
    proxy = ipproxy()
    retry = 3
    headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8", 
    "Accept-Encoding": "gzip, deflate", 
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8", 
    "Cache-Control": "max-age=0", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
  }
    agent_list = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
                    "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
                    "Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko ) Version/5.1 Mobile/9B176 Safari/7534.48.3",
                    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
                    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; ja-jp) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
                    "Mozilla/5.0 (Android 2.2; Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4",
                    "Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0",
                    "Mozilla/5.0 (X11; Linux i586; rv:63.0) Gecko/20100101 Firefox/63.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:10.0) Gecko/20100101 Firefox/62.0",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/58.0",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
                    ]

    @classmethod
    def get(cls, url,*args,**kwargs):###给requests.get请求添加headers和代理
        print("in customized get")
        session = requests.Session()
        session.cookies.set_policy(BlockAll()) ##屏蔽cookies
        print("test headers and proxies")
        headers = custom_requests.get_headers()
        proxies = custom_requests.get_proxy()
        # pool = ProxyManager(proxy_url = proxy_url,headers = headers)
        # print(proxies)
        # resp = requests.get(url = "http://httpbin.org/get",headers = headers, proxies = proxies)
        # print(resp.text)
        # return requests.get(url = url,headers = headers,proxies =proxies,*args,**kwargs)
        try : 
            resp = session.get(url = url,proxies = proxies,*args,**kwargs)
        except ProxyError as e:
            print("counter a proxy error,try ", cls.retry)
            print(e)
            if cls.retry > 0 :
                resp = cls.get(url =url )
                cls.retry = cls.retry -1 
            else:
                resp = None
                cls.retry = 3
        return resp



    @classmethod
    def get_proxy(cls):##获取代理
        proxies = {}
        proxy_ip = custom_requests.proxy.get().decode()
        proxies["http"] = "http://"+proxy_ip
        return proxies


    @classmethod
    def get_headers(cls):##获取头部
        pos = np.random.randint(len(custom_requests.agent_list))
        agent = custom_requests.agent_list[pos]
        custom_requests.headers["User-Agent"] = agent
        return custom_requests.headers

class req_crawler(object):##req爬虫主类，管理爬虫线程
    root_url = "http://www.yelp.com"
    END_FLAG =False
    def __init__(self):
        self.db = None
        self.all_cities = {}
        self.thread_db = {}
        self.output = queue.Queue()
        self._get_cities()
    

    def _get_cities(self):##获取所有城市的信息
        print("trying to get all the cities")
        loc_url = req_crawler.root_url+"/locations"
        print(loc_url)
        r = custom_requests.get(loc_url)
        if r.status_code!=200:
            self.handle_status_code(loc_url)
        html = BeautifulSoup(r.text,features = "html.parser")
        region = html.find_all(name = "ul",attrs={"class":"cities"})
        for reg in region:
            cities = reg.find_all(name = "a")
            for ci in cities:
                self.all_cities[ci.text] = req_crawler.root_url+ci.attrs["href"]

    # def handle(self):
    #     self.create_db(database())
    #     for k,v in self.all_cities.items():
    #         td = handle_thread(k,v,self.output)
    #         self.thread_db[k] = td
    #         td.start()
    #         print("start "+k+"!")
    #     while(self.threads_alive()):
    #         if self.output.empty():
    #             sleep(0.01)
    #         else:
    #             data = self.output.get()
    #             self.insert_data(data)  ###concurrent version

    def handle_single(self):##启动单线程爬取数据
        self.create_db(database())
        for k,v in self.all_cities.items():
            print("new a thread to handle  city ", k)
            td = handle_thread(k,v,self.output)
            td.start()
            td.join()
            self.insert_data()
            if req_crawler.END_FLAG:
                return

    def insert_data(self):##从输出队列中获取数据并插入数据库中
        data = self.output.get()
        for datalist in data:
            self.db.insert(datalist)


        
    def threads_alive(self):##判断线程状态
        initial_status = False
        status = initial_status
        for k,v in self.thread_db.items():
            status = initial_status or v.is_alive()
        return status


        
    def create_db(self,conn):
        """
        连接到数据库
        Args:
            conn: sqlite3.Connection 类型，即将使用的数据库连接
        """
        assert isinstance(conn,database), 'wrong db type'
        conn._createdb()
        conn.connect()
        self.db = conn

    def handle_status_code(self,url,retry = 3):##处理错误请求
        status_code = -1
        while retry>0 and status_code!=200 :
            resp = custom_requests.get(url)
            status_code = resp.status_code
            print("trying : ",resp.status_code)
            retry = retry -1
        return resp


class handle_thread(threading.Thread):###爬取页面的线程
    def __init__(self,city,url,output):
        threading.Thread.__init__(self,name = city)
        self.count = 0
        self.thread_name = city
        self.root_url = self._find_root(url)
        self.output = output
     

    
    def _find_root(self,url):##找到餐厅信息的入口，获取一个城市餐厅url的模板
        print("try to find the restaurant entry of city %s", self.thread_name)
        resp = custom_requests.get(url)
        try:
            assert resp.status_code ==200, url + "  status_code = " + str(resp.status_code)
        except AssertionError as e :
            resp = self.handle_status_code(url)
        html = BeautifulSoup(resp.text,features = "html.parser")
        nodes = html.find_all(name = "a",attrs ={"class":"homepage-hero_link"})
        try : 
            restaurant = nodes[1]
            assert_info = "faild to find restaurants in " + url
            assert restaurant.text=="Restaurants", assert_info
        except Exception as e:
            print("faild to find restaurants in " + url)
        return req_crawler.root_url + restaurant.attrs["href"]


    def run(self):#handle_thread程序入口，开始执行
        page = self.next_page()##获取start=0 的页面
        while self.not_end(page):##循环执行，获取页面
            self.handle_page(page)
            page = self.next_page()


    def handle_status_code(self,url,retry = 3):##遇到请求成功的情况需要重新请求
        status_code = -1
        while retry>0 and status_code!=200 :
            resp = custom_requests.get(url)
            status_code = resp.status_code
            print("trying :",resp.status_code, self.thread_name)
            retry = retry -1
        return resp



    def next_page(self):##跳转到下一页面，并获取下一页面的信息
        print("jump to next page ")
        time.sleep(3)
        page_url = self.root_url + "&start="+str(self.count)
        self.count = self.count +30
        resp = custom_requests.get(page_url)
        if resp.status_code!=200:
            resp = self.handle_status_code(page_url)
        page = BeautifulSoup(resp.text,features = "html.parser")
        try:
            wrap = page.find(name = "div",attrs = {"id":"wrap"})
            assert wrap!=None, "the page goes wrong retry"
            with open("errorpage.html","w",encoding = "utf-8") as file:
                file.write(page.text)
        except AssertionError as e :
            self.count = self.count - 30
            self.next_page()
        return page

        
    def not_end(self,page):##判断是否已经遍历完该城市的所有餐厅信息
        node = page.find(name = "h3",attrs = {"class":"lemon--h3__373c0__sQmiG heading--h3__373c0__1n4Of"})
        if node and node.text=="We\'re sorry, the page of results you requested is unavailable.":
            print(self.thread_name + " reaches end page" + str(self.count))
            return False
        if time.clock() >300:
            req_crawler.END_FLAG = True
            return False
        else: 
            return True


    def handle_page(self,page):##解析一个餐厅的BeautifulSoup信息页面
        print("in handling a page")
        data = []
        wrap = page.find(name = "div",attrs = {"id":"wrap"})
        region = wrap.findChild(name = "div",attrs={"role":"region"})
        unsort_list = region.findChildren(name = "div",recursive = False)[1].find(name = "ul")
        eles = unsort_list.find_all(name = "li",recursive = False)
        for index,res in enumerate(eles):
            try:
                datalist = self._parse_one_restaurant(self.thread_name,res)##解析餐厅元素信息
                data.append(datalist)
            except Exception as e:
                print("handling {} page{} the {}th restaurant goes wrong!!".format(self.thread_name, self.count,index))
                print(e)
        self.output.put(data)
        print("already put data of {} in page {} to Queue".format(self.thread_name,self.count))


    def _parse_one_restaurant(self,cityname,ele):##从一个餐厅元素里面提取出餐厅信息。
        """
        处理从网页中获得的餐厅element
        Args:
            cityname: str类型，城市名称
            ele: FirefoxWebElement类型，代表一个餐厅
        return:
            datalist：以列表的形式返回餐厅的信息，长度为7 里面元素可能为None
        """
        res_name = None
        location = None
        price = None 
        rate = None 
        reviews = None
        img_url = None
        self.ele =ele #for testing 
        res_num = ele.find(name = 'h3').text.split('.\xa0')[0]##餐厅的编码，用于报错使用
        res_name = ele.find(name = 'h3').text.split('.\xa0')[1]##获取餐馆的名字
        try:
            reviews = ele.find(name ="span" , attrs = {"class":'lemon--span__373c0__3997G text__373c0__2pB8f reviewCount__373c0__2r4xT text-color--mid__373c0__3G312 text-align--left__373c0__2pnx_'})
            reviews = int(reviews.text.split(' ')[0])##获取餐馆的评论数量
            price = ele.find(name = "span",attrs = {"class":'lemon--span__373c0__3997G text__373c0__2pB8f priceRange__373c0__2DY87 text-color--normal__373c0__K_MKN text-align--left__373c0__2pnx_ text-bullet--after__373c0__1ZHaA'})
            price = len(price.text.split('$'))-1 ##获取餐厅的价格等级
            ##获得餐厅地点信息
            location = ele.find_all(name = "div",attrs = {"class":'lemon--div__373c0__1mboc display--inline-block__373c0__2de_K u-space-t1 border-color--default__373c0__2oFDT'})[1]
            location = location.text##有时无法找到地点信息
            rate=ele.find(name = "div",attrs = {"role":'img'})
            rate = float(rate.attrs['aria-label'].split(' ')[0])
            img  = ele.find(name = 'img')
            img_url = str(img.attrs['src'])
        except AttributeError as e:##处理爬取过程中的异常
            pass
            # print(cityname,res_num)
            # print(e)
            # print(sys.exc_info())
        except IndexError as e:
            pass
            # print(cityname,res_num)
            # print(e)
        except: 
            raise
        datalist = [res_name,cityname,location,price,rate,reviews,img_url]
        return datalist