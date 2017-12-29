import requests
import pkg_resources


class Version:
    PYPI_URL = "https://pypi.python.org/pypi/hackertray/json"

    @staticmethod
    def latest():
        res = requests.get(Version.PYPI_URL).json()
        return res['info']['version']

    @staticmethod
    def current():
        return pkg_resources.require("hackertray")[0].version

    @staticmethod
    def new_available():
        latest = Version.latest()
        current = Version.current()
        try:
            if pkg_resources.parse_version(latest) > pkg_resources.parse_version(current):
                print("[+] New version " + latest + " is available")
                return True

            else:
                return False

        except requests.exceptions.RequestException as e:
            print("[+] There was an error in trying to fetch updates")
            return False
