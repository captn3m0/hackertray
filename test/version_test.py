import json
import unittest
from unittest import mock

from hackertray import Version


class VersionTest(unittest.TestCase):
    def test_latest(self):
        fake_response = json.dumps({"info": {"version": "9.9.9"}}).encode()
        with mock.patch("hackertray.version.urllib.request.urlopen") as m:
            m.return_value.__enter__ = lambda s: s
            m.return_value.__exit__ = mock.Mock(return_value=False)
            m.return_value.read.return_value = fake_response
            version = Version.latest()
        self.assertEqual(version, "9.9.9")

    def test_current(self):
        version = Version.current()
        self.assertIsInstance(version, str)


if __name__ == "__main__":
    unittest.main()
