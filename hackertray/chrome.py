import sqlite3
import shutil

class Chrome:
    @staticmethod
    def search(urls, config_folder_path):
        HackerNews.setup()
        conn = sqlite3.connect('/tmp/chrome')
        db = conn.cursor() 
        result = []
        for url in urls:
            db_result = db.execute('SELECT url from urls WHERE url=:url',{"url":url})
            if(db.fetchone() == None):
                result.append(False)
            else:
                result.append(True)
        return result
    @staticmethod
    def setup():
        shutil.copyfile(config_folder_path+'/History', '/tmp/hackertray.chrome')