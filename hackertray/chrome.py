
import sqlite3
import shutil
import os
import sys


class Chrome:
    HISTORY_TMP_LOCATION = '/tmp/hackertray.chrome'

    @staticmethod
    def search(urls, config_folder_path):
        Chrome.setup(config_folder_path)
        conn = sqlite3.connect(Chrome.HISTORY_TMP_LOCATION)
        db = conn.cursor()
        result = []
        for url in urls:
            db_result = db.execute('SELECT url from urls WHERE url=:url', {"url": url})
            if(db.fetchone() == None):
                result.append(False)
            else:
                result.append(True)
        os.remove(Chrome.HISTORY_TMP_LOCATION)
        return result

    @staticmethod
    def setup(config_folder_path):
        file_name = os.path.abspath(config_folder_path+'/History')
        if not os.path.isfile(file_name):
            print("ERROR: ", "Could not find Chrome history file", file=sys.stderr)
            sys.exit(1)
        shutil.copyfile(file_name, Chrome.HISTORY_TMP_LOCATION)
