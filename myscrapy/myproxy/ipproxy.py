import requests
class ipproxy(object):
	def __init__(self):
		pass
	def get(self):
		return requests.get("http://127.0.0.1:5010/get/").content##获取一个代理
	def delete(self,proxy):
		requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))##删除代理，基本用不到

if __name__ == '__main__':
	proxy = ipproxy()
	print(proxy.get().decode())

