import random
import requests

urls = [
	'http://node-hnapi-eu.herokuapp.com/', # Heroku (EU)
	'http://node-hnapi.azurewebsites.net/', # Windows Azure (North EU)
	'http://node-hnapi-asia.azurewebsites.net/', # Windows Azure (East Asia)
	'http://node-hnapi-eus.azurewebsites.net/', # Windows Azure (East US)
	'http://node-hnapi-weu.azurewebsites.net/', # Windows Azure (West EU)
	'http://node-hnapi-wus.azurewebsites.net/', # Windows Azure (West US)
	'http://node-hnapi-ncus.azurewebsites.net/' # Windows Azure (North Central US)
];

class HackerNews:
	@staticmethod
	def getHomePage():
		random.shuffle(urls)
		for i in urls:
			r = requests.get(i+"news")
			try:
				return r.json()
			except ValueError:
				continue;
			finally:
				print i