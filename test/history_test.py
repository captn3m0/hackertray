import unittest
import tempfile
import shutil
from pathlib import Path

from hackertray.history import (
    HistoryDB,
    HistorySchema,
    DatabaseError,
    discover,
    search,
    _query_urls,
)

FIXTURES = Path(__file__).parent


class TestChromiumSearch(unittest.TestCase):
    def setUp(self):
        self.db = HistoryDB(
            label="Chrome", schema=HistorySchema.CHROMIUM, path=FIXTURES / "History"
        )

    def test_search_matches(self):
        found = self.db.search(
            [
                "https://github.com/",
                "https://news.ycombinator.com/",
                "https://github.com/captn3m0/hackertray",
                "http://invalid_url/",
            ]
        )
        self.assertEqual(
            found,
            {
                "https://github.com/",
                "https://news.ycombinator.com/",
                "https://github.com/captn3m0/hackertray",
            },
        )

    def test_empty_urls(self):
        self.assertEqual(self.db.search([]), set())

    def test_no_matches(self):
        found = self.db.search(
            [
                "https://nonexistent.example.com/",
                "https://also-not-there.example.org/page",
            ]
        )
        self.assertEqual(found, set())

    def test_missing_db_raises(self):
        db = HistoryDB(
            label="Chrome",
            schema=HistorySchema.CHROMIUM,
            path=Path("/nonexistent/History"),
        )
        with self.assertRaises(DatabaseError):
            db.search(["https://example.com/"])

    def test_copied_fixture(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(FIXTURES / "History", Path(tmpdir) / "History")
            db = HistoryDB(
                label="Chrome",
                schema=HistorySchema.CHROMIUM,
                path=Path(tmpdir) / "History",
            )
            found = db.search(["https://github.com/", "http://invalid_url/"])
            self.assertEqual(found, {"https://github.com/"})


class TestFirefoxSearch(unittest.TestCase):
    def setUp(self):
        self.db = HistoryDB(
            label="Firefox",
            schema=HistorySchema.FIREFOX,
            path=FIXTURES / "places.sqlite",
        )

    def test_search_matches(self):
        found = self.db.search(
            [
                "http://www.hckrnews.com/",
                "http://www.google.com/",
                "http://wiki.ubuntu.com/",
                "http://invalid_url/",
            ]
        )
        self.assertEqual(
            found,
            {
                "http://www.hckrnews.com/",
                "http://www.google.com/",
                "http://wiki.ubuntu.com/",
            },
        )

    def test_copied_fixture(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(FIXTURES / "places.sqlite", Path(tmpdir) / "places.sqlite")
            db = HistoryDB(
                label="Firefox",
                schema=HistorySchema.FIREFOX,
                path=Path(tmpdir) / "places.sqlite",
            )
            found = db.search(["http://www.hckrnews.com/", "http://invalid_url/"])
            self.assertEqual(found, {"http://www.hckrnews.com/"})


class TestSafariSearch(unittest.TestCase):
    def setUp(self):
        self.db = HistoryDB(
            label="Safari",
            schema=HistorySchema.SAFARI,
            path=FIXTURES / "safari" / "History.db",
        )

    def test_search_matches(self):
        found = self.db.search(
            [
                "https://github.com/",
                "https://news.ycombinator.com/",
                "https://example.com/test",
                "https://nonexistent.example.com/",
            ]
        )
        self.assertEqual(
            found,
            {
                "https://github.com/",
                "https://news.ycombinator.com/",
                "https://example.com/test",
            },
        )

    def test_empty_urls(self):
        self.assertEqual(self.db.search([]), set())

    def test_no_matches(self):
        found = self.db.search(["https://nothing.example.com/"])
        self.assertEqual(found, set())

    def test_missing_db_raises(self):
        db = HistoryDB(
            label="Safari",
            schema=HistorySchema.SAFARI,
            path=Path("/nonexistent/History.db"),
        )
        with self.assertRaises(DatabaseError):
            db.search(["https://example.com/"])


class TestDiscover(unittest.TestCase):
    def _setup_and_discover(self, rel_path, fixture, platform):
        """Create a fake browser profile and run discover."""
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir) / "home"
            dest = home / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(FIXTURES / fixture, dest)
            return discover(home=home, platform=platform)

    def test_discover_finds_firefox_macos(self):
        dbs = self._setup_and_discover(
            "Library/Application Support/Firefox/abc12345.default-release/places.sqlite",
            "places.sqlite", "macos")
        firefox_dbs = [db for db in dbs if db.label == "Firefox"]
        self.assertEqual(len(firefox_dbs), 1)
        self.assertEqual(firefox_dbs[0].schema, HistorySchema.FIREFOX)

    def test_discover_finds_firefox_linux(self):
        dbs = self._setup_and_discover(
            ".mozilla/firefox/abc12345.default-release/places.sqlite",
            "places.sqlite", "linux")
        firefox_dbs = [db for db in dbs if db.label == "Firefox"]
        self.assertEqual(len(firefox_dbs), 1)
        self.assertEqual(firefox_dbs[0].schema, HistorySchema.FIREFOX)

    def test_discover_finds_chrome_macos(self):
        dbs = self._setup_and_discover(
            "Library/Application Support/Google/Chrome/Default/History",
            "History", "macos")
        chrome_dbs = [db for db in dbs if db.label == "Chrome"]
        self.assertEqual(len(chrome_dbs), 1)
        self.assertEqual(chrome_dbs[0].schema, HistorySchema.CHROMIUM)

    def test_discover_finds_chrome_linux(self):
        dbs = self._setup_and_discover(
            ".config/google-chrome/Default/History",
            "History", "linux")
        chrome_dbs = [db for db in dbs if db.label == "Chrome"]
        self.assertEqual(len(chrome_dbs), 1)
        self.assertEqual(chrome_dbs[0].schema, HistorySchema.CHROMIUM)

    def test_discover_finds_safari(self):
        dbs = self._setup_and_discover(
            "Library/Safari/History.db",
            "safari/History.db", "macos")
        safari_dbs = [db for db in dbs if db.label == "Safari"]
        self.assertEqual(len(safari_dbs), 1)
        self.assertEqual(safari_dbs[0].schema, HistorySchema.SAFARI)

    def test_discover_empty_home(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir) / "emptyhome"
            home.mkdir()
            for platform in ("macos", "linux"):
                dbs = discover(home=home, platform=platform)
                self.assertEqual(dbs, [])

    def test_discover_multiple_chrome_profiles_macos(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir) / "home"
            for profile in ("Default", "Profile 1"):
                d = home / "Library" / "Application Support" / "Google" / "Chrome" / profile
                d.mkdir(parents=True)
                shutil.copy(FIXTURES / "History", d / "History")
            dbs = discover(home=home, platform="macos")
            chrome_dbs = [db for db in dbs if db.label == "Chrome"]
            self.assertEqual(len(chrome_dbs), 2)

    def test_discover_multiple_chrome_profiles_linux(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir) / "home"
            for profile in ("Default", "Profile 1"):
                d = home / ".config" / "google-chrome" / profile
                d.mkdir(parents=True)
                shutil.copy(FIXTURES / "History", d / "History")
            dbs = discover(home=home, platform="linux")
            chrome_dbs = [db for db in dbs if db.label == "Chrome"]
            self.assertEqual(len(chrome_dbs), 2)


class TestSearch(unittest.TestCase):
    def test_search_empty_urls(self):
        self.assertEqual(search([]), set())

    def test_search_with_databases(self):
        db = HistoryDB(
            label="Chrome", schema=HistorySchema.CHROMIUM, path=FIXTURES / "History"
        )
        found = search(["https://github.com/", "http://nope.example.com/"], [db])
        self.assertEqual(found, {"https://github.com/"})

    def test_search_auto_discover(self):
        # With no databases installed in a fake home, returns empty
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir) / "empty"
            home.mkdir()
            found = search(["https://github.com/"], discover(home=home))
            self.assertEqual(found, set())

    def test_search_skips_broken_db(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_db = Path(tmpdir) / "History"
            bad_db.write_bytes(b"not a sqlite database")
            broken = HistoryDB(
                label="Broken", schema=HistorySchema.CHROMIUM, path=bad_db
            )
            good = HistoryDB(
                label="Chrome", schema=HistorySchema.CHROMIUM, path=FIXTURES / "History"
            )
            found = search(["https://github.com/"], [broken, good])
            self.assertEqual(found, {"https://github.com/"})

    def test_search_skips_missing_db(self):
        missing = HistoryDB(
            label="Gone",
            schema=HistorySchema.CHROMIUM,
            path=Path("/nonexistent/History"),
        )
        found = search(["https://github.com/"], [missing])
        self.assertEqual(found, set())


class TestQueryValidation(unittest.TestCase):
    def test_invalid_table_name(self):
        with self.assertRaises(ValueError, msg="Invalid table name"):
            _query_urls(FIXTURES / "History", "urls; DROP TABLE--", "url", ["x"])

    def test_invalid_column_name(self):
        with self.assertRaises(ValueError, msg="Invalid column name"):
            _query_urls(FIXTURES / "History", "urls", "url; DROP--", ["x"])

    def test_corrupt_file_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            f.write(b"not a sqlite database")
            f.flush()
            with self.assertRaises(DatabaseError):
                _query_urls(Path(f.name), "urls", "url", ["https://x.com/"])


class TestHistorySchema(unittest.TestCase):
    def test_chromium_schema(self):
        self.assertEqual(HistorySchema.CHROMIUM.db_file, "History")
        self.assertEqual(HistorySchema.CHROMIUM.table, "urls")
        self.assertEqual(HistorySchema.CHROMIUM.column, "url")

    def test_firefox_schema(self):
        self.assertEqual(HistorySchema.FIREFOX.db_file, "places.sqlite")
        self.assertEqual(HistorySchema.FIREFOX.table, "moz_places")

    def test_safari_schema(self):
        self.assertEqual(HistorySchema.SAFARI.db_file, "History.db")
        self.assertEqual(HistorySchema.SAFARI.table, "history_items")
