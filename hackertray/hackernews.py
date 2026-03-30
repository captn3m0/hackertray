import random
import json
import urllib.request

urls = [
    'https://node-hnapi.herokuapp.com/'
]


class HackerNews:

    @staticmethod
    def getHomePage():
        random.shuffle(urls)
        for i in urls:
            try:
                with urllib.request.urlopen(i + "news") as r:
                    return json.loads(r.read())
            except (ValueError, urllib.error.URLError):
                continue
