import unittest
import os
import pathlib
from pathlib import Path

from hackertray import Firefox

class FirefoxTest(unittest.TestCase):
    def test_history(self):
        config_folder_path = os.getcwd()+'/test/'
        data = Firefox.search([
            "http://www.hckrnews.com/",
            "http://www.google.com/",
            "http://wiki.ubuntu.com/",
            "http://invalid_url/"],
        config_folder_path)
        self.assertTrue(data == [True,True,True,False])

    def test_default(self):
        test_default_path = Path.home().joinpath(".mozilla/firefox/x0ran0o9.default")
        if(os.environ.get('TRAVIS') == 'true'):
            if not os.path.exists(test_default_path):
                os.makedirs(test_default_path)
            with open(str(Path.home().joinpath('.mozilla/firefox/profiles.ini')), 'w') as f:
                f.write("""
[Profile1]
Name=default
IsRelative=1
Path=x0ran0o9.default
Default=1
                """)
        self.assertTrue(Firefox.default_firefox_profile_path()==Path.home().joinpath(".mozilla/firefox/x0ran0o9.default"))
