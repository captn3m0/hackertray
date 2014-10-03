import unittest
import os

from hackertray import Chrome

class ChromeTest(unittest.TestCase):
    def runTest(self):
        config_folder_path = os.getcwd()+'/test/'
        data = Chrome.search([
            "https://github.com/",
            "https://news.ycombinator.com/",
            "https://github.com/captn3m0/hackertray",
            "http://invalid_url/"],
        config_folder_path)
        self.assertTrue(data == [True,True,True,False])