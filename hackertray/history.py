"""Browser history discovery and search.

Discovers all browser history databases on the system using glob patterns,
then searches them for visited URLs. Supports Chromium-based, Firefox-based,
and Safari browsers.
"""

from __future__ import annotations

import enum
import logging
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_IS_MACOS = sys.platform == "darwin"
_IS_LINUX = sys.platform.startswith("linux")

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


# ── Schema types ──────────────────────────────────────────────────────


class HistorySchema(enum.Enum):
    """Database schema for a browser family."""

    CHROMIUM = ("History", "urls", "url")
    FIREFOX = ("places.sqlite", "moz_places", "url")
    SAFARI = ("History.db", "history_items", "url")

    def __init__(self, db_file: str, table: str, column: str):
        self.db_file = db_file
        self.table = table
        self.column = column


# ── Glob-based discovery ──────────────────────────────────────────────

# Each entry: (schema, label, {platform: [glob patterns relative to ~]})
# Globs use * to match any profile directory.

_BROWSERS: list[tuple[HistorySchema, str, dict[str, list[str]]]] = [
    # Chromium-based
    (
        HistorySchema.CHROMIUM,
        "Chrome",
        {
            "macos": ["Library/Application Support/Google/Chrome/*/History"],
            "linux": [".config/google-chrome/*/History"],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Chromium",
        {
            "macos": ["Library/Application Support/Chromium/*/History"],
            "linux": [".config/chromium/*/History"],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Brave",
        {
            "macos": [
                "Library/Application Support/BraveSoftware/Brave-Browser/*/History"
            ],
            "linux": [".config/BraveSoftware/Brave-Browser/*/History"],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Edge",
        {
            "macos": ["Library/Application Support/Microsoft Edge/*/History"],
            "linux": [
                ".config/microsoft-edge/*/History",
                ".config/microsoft-edge-dev/*/History",
            ],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Vivaldi",
        {
            "macos": ["Library/Application Support/Vivaldi/*/History"],
            "linux": [".config/vivaldi/*/History"],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Arc",
        {
            "macos": ["Library/Application Support/Arc/User Data/*/History"],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Opera",
        {
            "macos": ["Library/Application Support/com.operasoftware.Opera/History"],
            "linux": [".config/opera/History"],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Opera GX",
        {
            "macos": ["Library/Application Support/com.operasoftware.OperaGX/History"],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Yandex",
        {
            "macos": ["Library/Application Support/Yandex/YandexBrowser/*/History"],
            "linux": [".config/yandex-browser/*/History"],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Sidekick",
        {
            "macos": ["Library/Application Support/Sidekick/*/History"],
            "linux": [".config/sidekick/*/History"],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Thorium",
        {
            "macos": ["Library/Application Support/Thorium/*/History"],
            "linux": [".config/thorium/*/History"],
        },
    ),
    (
        HistorySchema.CHROMIUM,
        "Epic",
        {
            "macos": ["Library/Application Support/HiddenReflex/Epic/*/History"],
        },
    ),
    # Firefox-based
    (
        HistorySchema.FIREFOX,
        "Firefox",
        {
            "macos": [
                "Library/Application Support/Firefox/Profiles/*/places.sqlite",
                "Library/Application Support/Firefox/*/places.sqlite",
            ],
            "linux": [
                ".mozilla/firefox/*/places.sqlite",
                ".var/app/org.mozilla.firefox/.mozilla/firefox/*/places.sqlite",
            ],
        },
    ),
    (
        HistorySchema.FIREFOX,
        "LibreWolf",
        {
            "macos": ["Library/Application Support/LibreWolf/*/places.sqlite"],
            "linux": [
                ".librewolf/*/places.sqlite",
                ".var/app/io.gitlab.librewolf-community/.librewolf/*/places.sqlite",
            ],
        },
    ),
    (
        HistorySchema.FIREFOX,
        "Waterfox",
        {
            "macos": ["Library/Application Support/Waterfox/*/places.sqlite"],
            "linux": [".waterfox/*/places.sqlite"],
        },
    ),
    (
        HistorySchema.FIREFOX,
        "Zen",
        {
            "macos": [
                "Library/Application Support/zen/Profiles/*/places.sqlite",
                "Library/Application Support/zen/*/places.sqlite",
            ],
            "linux": [".zen/*/places.sqlite"],
        },
    ),
    (
        HistorySchema.FIREFOX,
        "Floorp",
        {
            "macos": ["Library/Application Support/Floorp/*/places.sqlite"],
            "linux": [".floorp/*/places.sqlite"],
        },
    ),
    # Safari
    (
        HistorySchema.SAFARI,
        "Safari",
        {
            "macos": ["Library/Safari/History.db"],
        },
    ),
]

_PLATFORM_KEY = "macos" if _IS_MACOS else "linux" if _IS_LINUX else None


# ── Database access ───────────────────────────────────────────────────


class DatabaseError(Exception):
    """Raised when a history database cannot be read."""


@dataclass(frozen=True)
class HistoryDB:
    """A discovered browser history database."""

    label: str
    schema: HistorySchema
    path: Path

    def search(self, urls: list[str]) -> set[str]:
        """Return the subset of urls found in this history database."""
        if not urls:
            return set()
        return _query_urls(self.path, self.schema.table, self.schema.column, urls)


def _open_readonly(db_path: Path) -> sqlite3.Connection:
    """Copy a database to memory to avoid lock contention."""
    fd, tmp_path = tempfile.mkstemp(prefix="hackertray_")
    try:
        os.close(fd)
        shutil.copyfile(db_path, tmp_path)
        src = sqlite3.connect(tmp_path)
        conn = sqlite3.connect(":memory:")
        src.backup(conn)
        src.close()
    except (OSError, sqlite3.Error) as e:
        raise DatabaseError(f"Failed to read {db_path}: {e}") from e
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    return conn


def _query_urls(db_path: Path, table: str, column: str, urls: list[str]) -> set[str]:
    """Check which URLs exist in a browser history SQLite database."""
    if not _IDENTIFIER_RE.match(table):
        raise ValueError(f"Invalid table name: {table!r}")
    if not _IDENTIFIER_RE.match(column):
        raise ValueError(f"Invalid column name: {column!r}")

    if not db_path.is_file():
        raise DatabaseError(f"History database not found: {db_path}")

    conn = _open_readonly(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE TEMP TABLE _ht_lookup (url TEXT PRIMARY KEY)")
        cursor.executemany(
            "INSERT OR IGNORE INTO _ht_lookup (url) VALUES (?)", [(u,) for u in urls]
        )
        query = f'SELECT l.url FROM _ht_lookup l INNER JOIN "{table}" h ON l.url = h."{column}"'
        return {row[0] for row in cursor.execute(query)}
    finally:
        conn.close()


# ── Public API ────────────────────────────────────────────────────────


def discover(home: Path | None = None, platform: str | None = None) -> list[HistoryDB]:
    """Discover all browser history databases on this system.

    Returns a list of HistoryDB instances, one per database file found.
    """
    if home is None:
        home = Path.home()

    key = platform or _PLATFORM_KEY
    results: list[HistoryDB] = []
    for schema, label, platform_globs in _BROWSERS:
        patterns = platform_globs.get(key, []) if key else []
        for pattern in patterns:
            for db_path in sorted(home.glob(pattern)):
                if db_path.is_file():
                    logger.debug("Found %s history: %s", label, db_path)
                    results.append(HistoryDB(label=label, schema=schema, path=db_path))
    return results


def search(urls: list[str], databases: list[HistoryDB] | None = None) -> set[str]:
    """Search browser history for the given URLs.

    Args:
        urls: URLs to look up.
        databases: Databases to search. If None, discovers all databases.

    Returns:
        Set of URLs found in any browser's history.
    """
    if not urls:
        return set()

    if databases is None:
        databases = discover()

    found: set[str] = set()
    for db in databases:
        try:
            found |= db.search(urls)
        except (DatabaseError, Exception) as e:
            logger.debug("Error searching %s (%s): %s", db.label, db.path, e)
            continue
    return found
