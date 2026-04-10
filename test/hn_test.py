import json
import unittest
from pathlib import Path
from unittest import mock

from hackertray import HackerNews

FIXTURE = json.loads((Path(__file__).parent / "news_fixture.json").read_text())


class HNTest(unittest.TestCase):
    def test_parses_stories(self):
        with mock.patch("hackertray.hackernews.urllib.request.urlopen") as m:
            m.return_value.__enter__ = lambda s: s
            m.return_value.__exit__ = mock.Mock(return_value=False)
            m.return_value.read.return_value = json.dumps(FIXTURE).encode()

            data = HackerNews.getHomePage()

        self.assertEqual(len(data), len(FIXTURE))
        self.assertEqual(data[0]["id"], FIXTURE[0]["id"])
        self.assertEqual(data[0]["title"], FIXTURE[0]["title"])

    def test_items_have_required_fields(self):
        for item in FIXTURE:
            self.assertIn("id", item)
            self.assertIn("title", item)
            self.assertIn("url", item)
            self.assertIn("points", item)
            self.assertIn("comments_count", item)


if __name__ == "__main__":
    unittest.main()
