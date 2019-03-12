# -*- coding: utf-8 -*-
import sys
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from mydb import database
import time


class selecrawler():
    def __init__(self):
        self.db = None
        self.driver = Firefox()
        self.driver.implicitly_wait(1)##设定获取资源时间为一秒
        self.citydict = {}
        self.wait  = WebDriverWait(self.driver, 5)##让浏览器最多显示等待5秒
        
    def get_all_cities(self):
        """
        从yelp网站中获取所有城市的url信息
        """
        url = 'https://www.yelp.com/locations'
        self.driver.get(url)
        cities = self.driver.find_elements_by_class_name('cities')
        for city in cities:
            city = city.find_element_by_tag_name('a')
            cityname = str(city.text)     #获取城市的名字
            cityurl = city.get_property('href')#获取城市的访问地址
            self.citydict[cityname] = cityurl
        
    def handle_onecity(self, cityname:str,cityurl:str):
        """
        爬去一个城市的数据
        Args:
            cityname: str类型 即将爬去的城市的名称
            cityurl: str类型 城市的url地址
        """
        self.driver.get(cityurl)
        ##导航到餐厅页面
        res = self.driver.find_element_by_css_selector('li.homepage-hero_category:nth-child(2) > div:nth-child(1) > a:nth-child(2)')
        ori_url = res.get_property('href')
        print(ori_url)
        print(res.text)
        count = 0
        resurl = ori_url+'&start='+str(count)
        self.driver.get(resurl)
        data = []
        while True and time.clock()<300:
            try:
                ress = self.driver.find_element_by_css_selector('ul.undefined:nth-child(1)')##等待餐厅列表的出现
                reslist = ress.find_elements_by_tag_name('li')
                assert len(reslist)!=0, 'restaurant list is empty!'
                for index,res in enumerate(reslist):
                    try:
                        datalist = self._parse_one_restaurant(cityname,res)
                        data.append(datalist)
                    except Exception as e:
                        print("handling {} page {} the {}th restaurant goes wrong!!".format(cityname, count,index))
                        print(e)
                        print(sys.exc_info())
                count+=30
                resurl = ori_url+'&start='+str(count)#找到下一个的url
                self.driver.get(resurl)       
                #self.driver.execute_script("scrollTo(0,7500);")
                #condition = ec.presence_of_element_located((By.CSS_SELECTOR,'.navigation-button-container__373c0__2sEbf'))#期待Next导航栏出现
                #next_button = self.wait.until(condition)##跳转到下一页中
                #nx_url = next_button.find_element_by_tag_name('a').get_property('href')
                #print(nx_url)
                #self.driver.get(nx_url)
                #self.driver.execute_script("arguments[0].click();",next_button)
                #ActionChains(self.driver).move_to_element(next_button).click(next_button).perform()
            except NoSuchElementException as e:
                ##判断是否已经到了城市餐厅的末尾
                theend = self.wait.until(ec.text_to_be_present_in_element((By.CSS_SELECTOR,'.lemon--h3__373c0__5Q5tF'),'We\'re sorry, the page of results you requested is unavailable.'))
                if theend:
                    print('have reached the end of {}'.format(cityname))
                    break
                else:
                    print(e)
                    break
            except Exception as e:
                print("when handling city {} some thing unexpected happened")
                print(e)
        ##begin to insert data
        if self.db:
            for datalist in data:
                self.db.insert(datalist)
            print("already insert the data of {}".format(cityname))
        else:
            print("the crawler has not connected to db!")
            

    def _parse_one_restaurant(self,cityname,ele):
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
        res_num = ele.find_element_by_tag_name('h3').text.split('. ')[0]##餐厅的编码，用于报错使用
        res_name = ele.find_element_by_tag_name('h3').text.split('. ')[1]##获取餐馆的名字
        try:
            reviews = ele.find_element_by_css_selector("span[class='lemon--span__373c0__3997G text__373c0__2pB8f reviewCount__373c0__2r4xT text-color--mid__373c0__3G312 text-align--left__373c0__2pnx_']")
            reviews = int(reviews.text.split(' ')[0])##获取餐馆的评论数量
            price = ele.find_element_by_css_selector("div[class='lemon--div__373c0__1mboc priceCategory__373c0__3zW0R border-color--default__373c0__2oFDT']")
            price = len(price.text.split('$'))-1 ##获取餐厅的价格等级
            ##获得餐厅地点信息
            location = ele.find_element_by_tag_name(name="address")
            location = location.text##有时无法找到地点信息
            rate=ele.find_element_by_css_selector("div[role='img']")
            rate = float(rate.get_attribute('aria-label').split(' ')[0])
            img  = ele.find_element_by_tag_name('img')
            img_url = str(img.get_attribute('src'))
        except NoSuchElementException as e:##处理爬取过程中的异常
            print(cityname,res_num)
            print(e)
        except IndexError as e:
            print(cityname,res_num)
            print(e)
        except: 
            raise
        datalist = [res_name,cityname,location,price,rate,reviews,img_url]
        return datalist
    
    def connectdb(self,conn):
        """
        连接到数据库
        Args:
            conn: sqlite3.Connection 类型，即将使用的数据库连接
        """
        assert isinstance(conn,database), 'wrong db type'
        if conn.isconnected:
            self.db = conn
        else:
            conn.connect()
            self.db = conn