import unittest
from hackertray import Version

class VersionTest(unittest.TestCase):
    def runTest(self):
        version = Version.latest()
        assert version

if __name__ == '__main__':
    unittest.main()