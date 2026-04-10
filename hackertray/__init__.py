#!/usr/bin/env python

import os
import sys
import argparse
import configparser
import logging
from pathlib import Path

from .hackernews import HackerNews
from .version import Version

_IS_MACOS = sys.platform == "darwin"


def _load_config():
    """Load config from ~/.config/hackertray/hackertray.ini or ~/.config/hackertray.ini."""
    config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    candidates = [
        config_dir / "hackertray" / "hackertray.ini",
        config_dir / "hackertray.ini",
    ]

    cp = configparser.ConfigParser()
    for path in candidates:
        if path.is_file():
            cp.read(path)
            break

    if "hackertray" not in cp:
        return {}

    section = cp["hackertray"]
    defaults = {}

    # Boolean options
    for key in ("comments", "reverse", "verbose"):
        if key in section:
            defaults[key] = section.getboolean(key)
    if "macos-icon-color" in section:
        defaults["macos_icon_color"] = section["macos-icon-color"]

    return defaults


def main():
    parser = argparse.ArgumentParser(description="Hacker News in your System Tray")
    parser.add_argument("-v", "--version", action="version", version=Version.current())
    parser.add_argument(
        "-c",
        "--comments",
        dest="comments",
        default=False,
        action="store_true",
        help="Load the HN comments link for the article as well",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        dest="reverse",
        default=False,
        action="store_true",
        help="Reverse the order of items. Use if your status bar is at the bottom of the screen",
    )
    parser.add_argument(
        "--macos-icon-color",
        dest="macos_icon_color",
        default="orange",
        choices=["black", "white", "none", "orange", "green"],
        help="Status bar icon background color (macOS only)",
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="Enable debug logging",
    )

    # Load config file defaults, CLI flags take precedence
    config_defaults = _load_config()
    parser.set_defaults(**config_defaults)

    args = parser.parse_args()

    if _IS_MACOS:
        from .macos import main_macos

        main_macos(args)
    else:
        from .linux import HackerNewsApp

        indicator = HackerNewsApp(args)
        indicator.run()
