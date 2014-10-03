import unittest
import os

from hackertray import Firefox

class ChromeTest(unittest.TestCase):
    def runTest(self):
        config_folder_path = os.getcwd()+'/test/'
        data = Firefox.search([
            "http://www.hckrnews.com/",
            "http://www.google.com/",
            "http://wiki.ubuntu.com/",
            "http://invalid_url/"],
        config_folder_path)
        self.assertTrue(data == [True,True,True,False])