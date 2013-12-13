import unittest
from hackernews import HackerNews


class HNTest(unittest.TestCase):
    def runTest(self):
        data = HackerNews.getHomePage()
        self.assertTrue(len(data) > 0)


if __name__ == '__main__':
    unittest.main()