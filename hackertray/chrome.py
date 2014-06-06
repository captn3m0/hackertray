import sqlite3
import shutil
import os

class Chrome:
    @staticmethod
    def search(urls, config_folder_path):
        Chrome.setup(config_folder_path)
        conn = sqlite3.connect('/tmp/hackertray.chrome')
        db = conn.cursor() 
        result = []
        for url in urls:
            db_result = db.execute('SELECT url from urls WHERE url=:url',{"url":url})
            if(db.fetchone() == None):
                result.append(False)
            else:
                result.append(True)
        os.remove('/tmp/hackertray.chrome')
        return result
    @staticmethod
    def setup(config_folder_path):
        shutil.copyfile(config_folder_path+'/History', '/tmp/hackertray.chrome')