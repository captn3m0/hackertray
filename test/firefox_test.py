import unittest
import os
import tempfile
import shutil
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
        with tempfile.TemporaryDirectory() as tmpdir:
            firefox_dir = Path(tmpdir) / "mozilla" / "firefox"
            profile_dir = firefox_dir / "x0ran0o9.default"
            profile_dir.mkdir(parents=True)

            # Copy test places.sqlite into the fake profile
            shutil.copy(
                Path(__file__).parent / "places.sqlite",
                profile_dir / "places.sqlite",
            )

            profiles_ini = firefox_dir / "profiles.ini"
            profiles_ini.write_text(
                "[Profile1]\n"
                "Name=default\n"
                "IsRelative=1\n"
                "Path=x0ran0o9.default\n"
                "Default=1\n"
            )

            old_val = os.environ.get("XDG_CONFIG_HOME")
            try:
                os.environ["XDG_CONFIG_HOME"] = tmpdir
                result = Firefox.default_firefox_profile_path()
                self.assertEqual(result, str(profile_dir))
            finally:
                if old_val is None:
                    os.environ.pop("XDG_CONFIG_HOME", None)
                else:
                    os.environ["XDG_CONFIG_HOME"] = old_val
