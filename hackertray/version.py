import json
import urllib.request
import urllib.error
from importlib.metadata import version, PackageNotFoundError


class Version:
    PYPI_URL = "https://pypi.python.org/pypi/hackertray/json"

    @staticmethod
    def latest():
        with urllib.request.urlopen(Version.PYPI_URL) as r:
            return json.loads(r.read())["info"]["version"]

    @staticmethod
    def current():
        try:
            return version("hackertray")
        except PackageNotFoundError:
            return "unknown"

    @staticmethod
    def new_available():
        return False
        latest = Version.latest()
        current = Version.current()
        try:
            if pkg_resources.parse_version(latest) > pkg_resources.parse_version(
                current
            ):
                print("[+] New version " + latest + " is available")
                return True
            else:
                return False
        except urllib.error.URLError as e:
            print("[+] There was an error in trying to fetch updates")
            return False
