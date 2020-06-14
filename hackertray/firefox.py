
import sqlite3
import shutil
import os
import sys
from pathlib import Path
import configparser

class Firefox:
    HISTORY_TMP_LOCATION = '/tmp/hackertray.firefox'
    HISTORY_FILE_NAME = '/places.sqlite'

    @staticmethod
    def default_firefox_profile_path():
        profile_file_path = Path.home().joinpath(".mozilla/firefox/profiles.ini")
        profile_path = None
        if (os.path.exists(profile_file_path)):
            parser = configparser.ConfigParser()
            parser.read(profile_file_path)
            for section in parser.sections():
                if parser.has_option(section,"Default") and parser[section]["Default"] == "1":
                    if parser.has_option(section,"IsRelative") and parser[section]["IsRelative"] == "1":
                        profile_path = str(Path.home().joinpath(".mozilla/firefox/").joinpath(parser[section]["Path"]))
                    else:
                        profile_path = parser[section]["Path"]
        if profile_path and Path.is_dir(Path(profile_path)):
            return profile_path
        else:
            raise RuntimeError("Couldn't find default Firefox profile")

    @staticmethod
    def search(urls, config_folder_path):
        Firefox.setup(config_folder_path)
        conn = sqlite3.connect(Firefox.HISTORY_TMP_LOCATION)
        db = conn.cursor()
        result = []
        for url in urls:
            db_result = db.execute('SELECT url from moz_places WHERE url=:url', {"url": url})
            if(db.fetchone() == None):
                result.append(False)
            else:
                result.append(True)
        os.remove(Firefox.HISTORY_TMP_LOCATION)
        return result

    @staticmethod
    def setup(config_folder_path):
        file_name = os.path.abspath(config_folder_path + Firefox.HISTORY_FILE_NAME)
        if not os.path.isfile(file_name):
            print("ERROR: Could not find Firefox history file, using %s" % file_name)
            sys.exit(1)
        shutil.copyfile(file_name, Firefox.HISTORY_TMP_LOCATION)
