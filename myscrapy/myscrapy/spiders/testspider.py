import scrapy
class ProxyTestSpider(scrapy.Spider):
	name = "TestSpider"
	def start_requests(self):
		yield scrapy.Request(url = "http://httpbin.org/get",callback = self.parse,dont_filter = True)

	def parse(self,response):
		print("in parse")
		print(response.text)
		

