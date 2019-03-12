import scrapy
from bs4 import BeautifulSoup
import json
import time
class YelpSpider(scrapy.Spider):
    name = "YelpSpider"
    def __init__(self):##对象初始化函数
        super(YelpSpider,self).__init__()
        self.root_url = "https://www.yelp.com"
        self.all_cities = {}


    def start_requests(self):##开始获取第一个网页
        url = "https://www.yelp.com/locations"
        yield scrapy.Request(url = url, callback = self._get_all_cities)##发起一个网页请求，并使用回调函数回调


    def _get_all_cities(self,response):#处理返回来的响应页面，
        html = BeautifulSoup(response.text,features = "html.parser")
        region = html.find_all(name = "ul",attrs={"class":"cities"})##找到所有地点元素
        for reg in region:
            cities = reg.find_all(name = "a")
            for ci in cities:
                self.all_cities[ci.text] = self.root_url+ci.attrs["href"]##获取对应地点城市的url
        for k,v in self.all_cities.items():
            yield scrapy.Request(url = v, callback = self.handle_one, meta = {"cityname":k})##对每一个地点都发起一个请求


    def handle_one(self, response):##处理一个城市的请求
        if time.clock() >300:
            raise scrapy.exceptions.CloseSpider("time is up!")
        root = self._find_root(response)
        cityname = response.meta["cityname"]
        yield scrapy.Request(url = root, callback = self.parse, meta = {"cityname":cityname})


    def _find_root(self,resp):#所有餐厅信息的入口
        html = BeautifulSoup(resp.text,features = "html.parser")
        nodes = html.find_all(name = "a",attrs ={"class":"homepage-hero_link"})
        restaurant = nodes[1]
        assert_info = "faild to find restaurants in " + resp.url
        assert restaurant.text=="Restaurants", assert_info
        return self.root_url + restaurant.attrs["href"]+"&start=0"



    def parse(self,response):#解析一个餐厅信息页面，一个页面有30个餐厅的信息
        if time.clock() >300 :
            raise scrapy.exceptions.CloseSpider("time is up!")
        page = BeautifulSoup(response.text,features = "html.parser")##使用bs解析网页
        cityname = response.meta["cityname"]        
        nextpage , count = self.next_url(response.url)
        datadict = {}
        if self._not_end(page,cityname,count):
            data = self.handle_page(page,cityname,count)##解析页面函数
            datadict["data"] = data
            yield datadict
            yield scrapy.Request(url = nextpage,callback = self.parse,meta = {"cityname":cityname})


    def next_url(self,url):##跳转到下一个餐厅信息的页面
        data = url.split("&")
        assert len(data)==3, url
        start = data.pop(-1)
        count = int(start.split("=")[1])
        newurl = "&".join(data) + "&start="+str(count+30)
        return newurl,count




    def _not_end(self,page,cityname,count):##判断是否已经遍历完该城市的所有餐厅
        node = page.find(name = "h3",attrs = {"class":"lemon--h3__373c0__sQmiG heading--h3__373c0__1n4Of"})
        if node and node.text=="We\'re sorry, the page of results you requested is unavailable.":
            print(cityname + " reaches end page", "last start is: ",count)
            return False
        else:
             return True


    def handle_page(self,page,cityname,count):##解析beautifulSoup页面信息，并提取里面的餐厅信息
        wrap = page.find(name = "div",attrs = {"id":"wrap"})
        region = wrap.findChild(name = "div",attrs={"role":"region"})
        unsort_list = region.findChildren(name = "div",recursive = False)[1].find(name = "ul")
        eles = unsort_list.find_all(name = "li",recursive = False)
        data = []
        for index,res in enumerate(eles):
            try:
                datalist  = self._parse_one_restaurant(cityname,res)
                data.append(datalist)
            except Exception as e:
                print("handling {} page{} the {}th restaurant goes wrong!!".format(cityname, count,index))
                print(e)
        return data


    def _parse_one_restaurant(self,cityname,ele):##解析一个餐厅元素，提取餐厅信息
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
            # print(cityname,res_num,"AttributeError")
            # print(e)
            # print(sys.exc_info())
            pass
        except IndexError as e:
            pass
            # print(cityname,res_num,"IndexError")
            # print(e)
        except: 
            raise
        datalist = [res_name,cityname,location,price,rate,reviews,img_url]
        return datalist

# if __name__=="__main__":
#     sp = YelpSpider()
#     print(sp.next_url("https://www.yelp.com/search?cflt=restaurants&find_loc=Tokyo%2C+%E6%9D%B1%E4%BA%AC%E9%83%BD%2C+Japan&start=0"))


