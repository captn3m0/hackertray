import sqlite3
import shutil
import tempfile
import os
import sys
from pathlib import Path
import configparser

class Firefox:
    HISTORY_FILE_NAME = '/places.sqlite'

    @staticmethod
    def default_firefox_profile_path():
        config_home = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        firefox_dir = Path(config_home) / "mozilla" / "firefox"
        profile_file_path = firefox_dir / "profiles.ini"
        if not profile_file_path.exists():
            raise RuntimeError("Couldn't find Firefox profiles.ini")

        parser = configparser.ConfigParser()
        parser.read(profile_file_path)

        # Prefer the active install's locked profile (modern Firefox)
        for section in parser.sections():
            if section.startswith("Install") and parser.has_option(section, "Default"):
                rel_path = parser[section]["Default"]
                profile_path = firefox_dir / rel_path
                if profile_path.is_dir():
                    return str(profile_path)

        # Fall back to the section marked Default=1
        for section in parser.sections():
            if parser.has_option(section, "Default") and parser[section]["Default"] == "1":
                if parser.has_option(section, "IsRelative") and parser[section]["IsRelative"] == "1":
                    profile_path = firefox_dir / parser[section]["Path"]
                else:
                    profile_path = Path(parser[section]["Path"])
                if profile_path.is_dir():
                    return str(profile_path)

        raise RuntimeError("Couldn't find default Firefox profile")

    @staticmethod
    def search(urls, config_folder_path):
        file_name = os.path.abspath(config_folder_path + Firefox.HISTORY_FILE_NAME)
        if not os.path.isfile(file_name):
            print("ERROR: Could not find Firefox history file, using %s" % file_name)
            sys.exit(1)
        fd, tmp_path = tempfile.mkstemp(prefix='hackertray_firefox_')
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

        total = db.execute('SELECT COUNT(*) FROM moz_places').fetchone()[0]
        print(f"[firefox] loaded {total} rows from moz_places")

        result = []
        for url in urls:
            db.execute('SELECT url from moz_places WHERE url=:url', {"url": url})
            found = db.fetchone() is not None
            print(f"[firefox] {'HIT ' if found else 'MISS'} {url}")
            result.append(found)
        conn.close()
        return result
