from __future__ import print_function
import sqlite3
import shutil
import os
import sys


class Firefox:
    HISTORY_TMP_LOCATION = '/tmp/hackertray.firefox'
    HISTORY_FILE_NAME = '/places.sqlite'

    @staticmethod
    def search(urls, config_folder_path):
        Firefox.setup(config_folder_path)
        conn = sqlite3.connect(Firefox.HISTORY_TMP_LOCATION)
        db = conn.cursor()
        result = []
        for url in urls:
            # db_result = db.execute(
                # 'SELECT url from moz_places WHERE url=:url',{"url":url})
            if db.fetchone() is None:
                result.append(False)
            else:
                result.append(True)
        os.remove(Firefox.HISTORY_TMP_LOCATION)
        return result

    @staticmethod
    def setup(config_folder_path):
        file_name = os.path.abspath(
            config_folder_path + Firefox.HISTORY_FILE_NAME)
        if not os.path.isfile(file_name):
            print("ERROR: ", "Could not find Firefox history file", file=sys.stderr)
            sys.exit(1)
        shutil.copyfile(file_name, Firefox.HISTORY_TMP_LOCATION)
