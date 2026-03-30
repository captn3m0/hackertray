
import sqlite3
import shutil
import tempfile
import os
import sys


class Chrome:

    @staticmethod
    def search(urls, config_folder_path):
        file_name = os.path.abspath(config_folder_path + '/History')
        if not os.path.isfile(file_name):
            print("ERROR: Could not find Chrome history file", file=sys.stderr)
            sys.exit(1)
        fd, tmp_path = tempfile.mkstemp(prefix='hackertray_chrome_')
        try:
            os.close(fd)
            shutil.copyfile(file_name, tmp_path)
            src = sqlite3.connect(tmp_path)
            conn = sqlite3.connect(":memory:")
            src.backup(conn)
            src.close()
        finally:
            os.unlink(tmp_path)
        db = conn.cursor()
        result = []
        for url in urls:
            db.execute('SELECT url from urls WHERE url=:url', {"url": url})
            result.append(db.fetchone() is not None)
        conn.close()
        return result
