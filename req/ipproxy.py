import requests
class ipproxy(object):
	def __init__(self):
		pass
	def get(self):
		return requests.get("http://127.0.0.1:5010/get/").content
	def delete(self,proxy):
		requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

if __name__ == '__main__':
	proxy = ipproxy()
	print(proxy.get().decode())

