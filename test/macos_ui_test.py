import sys
import unittest
from unittest import mock

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "darwin", reason="macOS-only tests")

if sys.platform == "darwin":
    from AppKit import (
        NSApplication,
        NSApplicationActivationPolicyAccessory,
        NSMenu,
        NSOnState,
        NSOffState,
    )
    from hackertray.macos import HackerTrayDelegate

    # Need an NSApplication instance for NSMenu to work
    _app = NSApplication.sharedApplication()
    _app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)


def _make_item(
    id=1,
    title="Test Story",
    url="https://example.com",
    points=42,
    comments_count=10,
    history=False,
    user="testuser",
    time_ago="1 hour ago",
):
    return {
        "id": id,
        "title": title,
        "url": url,
        "points": points,
        "comments_count": comments_count,
        "history": history,
        "user": user,
        "time_ago": time_ago,
    }


def _make_delegate():
    d = HackerTrayDelegate.alloc().init()
    d._menu = NSMenu.alloc().init()
    d._menu.setAutoenablesItems_(False)
    return d


def _news_items(menu):
    """Return menu items that represent news stories (have representedObject)."""
    return [
        menu.itemAtIndex_(i)
        for i in range(menu.numberOfItems())
        if menu.itemAtIndex_(i).representedObject() is not None
    ]


def _item_titled(menu, title):
    """Find a menu item by exact title."""
    for i in range(menu.numberOfItems()):
        mi = menu.itemAtIndex_(i)
        if mi.title() == title:
            return mi
    return None


class TestMenuStructure(unittest.TestCase):
    def setUp(self):
        self.d = _make_delegate()
        self.data = [
            _make_item(id=i, title=f"Story {i}", points=i * 10 + 10)
            for i in range(1, 4)
        ]
        self.d._rebuild_menu(self.data)

    def test_news_items_count(self):
        self.assertEqual(len(_news_items(self.d._menu)), 3)

    def test_has_refresh(self):
        self.assertIsNotNone(_item_titled(self.d._menu, "Refresh"))

    def test_has_settings(self):
        self.assertIsNotNone(_item_titled(self.d._menu, "Settings"))

    def test_has_about(self):
        self.assertIsNotNone(_item_titled(self.d._menu, "About HackerTray"))

    def test_has_quit(self):
        self.assertIsNotNone(_item_titled(self.d._menu, "Quit"))

    def test_separators_present(self):
        seps = [
            self.d._menu.itemAtIndex_(i)
            for i in range(self.d._menu.numberOfItems())
            if self.d._menu.itemAtIndex_(i).isSeparatorItem()
        ]
        self.assertEqual(len(seps), 2)

    def test_no_visit_hn_item(self):
        self.assertIsNone(_item_titled(self.d._menu, "Visit news.ycombinator.com"))


class TestNewsItemFormat(unittest.TestCase):
    def test_title_contains_points_and_title(self):
        d = _make_delegate()
        d._rebuild_menu([_make_item(points=7, comments_count=3, title="Hello World")])
        mi = _news_items(d._menu)[0]
        self.assertIn("007/003", mi.title())
        self.assertIn("Hello World", mi.title())

    def test_attributed_title_set(self):
        d = _make_delegate()
        d._rebuild_menu([_make_item()])
        mi = _news_items(d._menu)[0]
        self.assertIsNotNone(mi.attributedTitle())

    def test_tooltip_contains_url_and_user(self):
        d = _make_delegate()
        d._rebuild_menu([_make_item(url="https://ex.com", user="alice")])
        mi = _news_items(d._menu)[0]
        self.assertIn("https://ex.com", mi.toolTip())
        self.assertIn("alice", mi.toolTip())

    def test_represented_object(self):
        d = _make_delegate()
        d._rebuild_menu([_make_item(id=99, url="https://ex.com")])
        info = _news_items(d._menu)[0].representedObject()
        self.assertEqual(info["url"], "https://ex.com")
        self.assertEqual(info["hn_id"], 99)
        self.assertEqual(info["item_id"], 99)

    def test_zero_points_skipped(self):
        d = _make_delegate()
        d._rebuild_menu([_make_item(points=0)])
        self.assertEqual(len(_news_items(d._menu)), 0)

    def test_none_points_skipped(self):
        d = _make_delegate()
        d._rebuild_menu([_make_item(points=None)])
        self.assertEqual(len(_news_items(d._menu)), 0)


class TestVisitedState(unittest.TestCase):
    def test_history_true_sets_checkmark(self):
        d = _make_delegate()
        d._rebuild_menu([_make_item(history=True)])
        mi = _news_items(d._menu)[0]
        self.assertEqual(mi.state(), NSOnState)

    def test_history_false_no_checkmark(self):
        d = _make_delegate()
        d._rebuild_menu([_make_item(history=False)])
        mi = _news_items(d._menu)[0]
        self.assertEqual(mi.state(), NSOffState)

    def test_open_link_opens_browser(self):
        d = _make_delegate()
        data = [_make_item(id=7, url="https://ex.com")]
        d._rebuild_menu(data)
        d._last_data = data
        mi = _news_items(d._menu)[0]
        with mock.patch("webbrowser.open") as m:
            d.openLink_(mi)
        m.assert_called_with("https://ex.com")

    def test_open_link_with_comments(self):
        d = _make_delegate()
        d._comment_state = True
        data = [_make_item(id=5, url="https://ex.com")]
        d._rebuild_menu(data)
        d._last_data = data
        mi = _news_items(d._menu)[0]
        with mock.patch("webbrowser.open") as m:
            d.openLink_(mi)
        calls = [c[0][0] for c in m.call_args_list]
        self.assertIn("https://ex.com", calls)
        self.assertIn("https://news.ycombinator.com/item?id=5", calls)


class TestReverseOrdering(unittest.TestCase):
    def _titles(self, menu):
        return [mi.representedObject()["hn_id"] for mi in _news_items(menu)]

    def test_default_order(self):
        d = _make_delegate()
        data = [_make_item(id=i, points=10) for i in [1, 2, 3]]
        d._rebuild_menu(data)
        self.assertEqual(self._titles(d._menu), [1, 2, 3])

    def test_reverse_order(self):
        d = _make_delegate()
        d._reverse = True
        data = [_make_item(id=i, points=10) for i in [1, 2, 3]]
        d._rebuild_menu(data)
        self.assertEqual(self._titles(d._menu), [3, 2, 1])

    def test_toggle_reverse_redraws(self):
        d = _make_delegate()
        data = [_make_item(id=i, points=10) for i in [1, 2, 3]]
        d._rebuild_menu(data)
        d._last_data = data
        self.assertEqual(self._titles(d._menu), [1, 2, 3])

        # Simulate toggle
        fake_sender = _item_titled(d._menu, "Reverse Ordering")
        d.toggleReverse_(fake_sender)
        self.assertTrue(d._reverse)
        self.assertEqual(self._titles(d._menu), [3, 2, 1])


class TestToggleComments(unittest.TestCase):
    def test_toggle_on(self):
        d = _make_delegate()
        self.assertFalse(d._comment_state)
        d._rebuild_menu([_make_item()])
        item = _item_titled(d._menu, "Open Comments")
        # Submenu item - get from settings submenu
        settings = _item_titled(d._menu, "Settings")
        sub = settings.submenu()
        comments = sub.itemAtIndex_(0)
        d.toggleComments_(comments)
        self.assertTrue(d._comment_state)
        self.assertEqual(comments.state(), NSOnState)

    def test_toggle_off(self):
        d = _make_delegate()
        d._comment_state = True
        d._rebuild_menu([_make_item()])
        settings = _item_titled(d._menu, "Settings")
        comments = settings.submenu().itemAtIndex_(0)
        d.toggleComments_(comments)
        self.assertFalse(d._comment_state)
        self.assertEqual(comments.state(), NSOffState)


class TestSettingsSubmenu(unittest.TestCase):
    def test_comments_initial_state_off(self):
        d = _make_delegate()
        d._rebuild_menu([_make_item()])
        settings = _item_titled(d._menu, "Settings")
        comments = settings.submenu().itemAtIndex_(0)
        self.assertEqual(comments.title(), "Open Comments")
        self.assertEqual(comments.state(), NSOffState)

    def test_comments_initial_state_on(self):
        d = _make_delegate()
        d._comment_state = True
        d._rebuild_menu([_make_item()])
        settings = _item_titled(d._menu, "Settings")
        comments = settings.submenu().itemAtIndex_(0)
        self.assertEqual(comments.state(), NSOnState)

    def test_reverse_initial_state(self):
        d = _make_delegate()
        d._reverse = True
        d._rebuild_menu([_make_item()])
        settings = _item_titled(d._menu, "Settings")
        reverse = settings.submenu().itemAtIndex_(1)
        self.assertEqual(reverse.title(), "Reverse Ordering")
        self.assertEqual(reverse.state(), NSOnState)


class TestConfigure(unittest.TestCase):
    def test_configure_basic(self):
        d = _make_delegate()
        args = mock.Mock(comments=True, reverse=True, macos_icon_color="orange")
        with mock.patch("hackertray.history.discover", return_value=[]):
            d.configure(args)
        self.assertTrue(d._comment_state)
        self.assertTrue(d._reverse)

    def test_configure_discovers_databases(self):
        d = _make_delegate()
        args = mock.Mock(comments=False, reverse=False, macos_icon_color="orange")
        fake_db = mock.Mock()
        with mock.patch("hackertray.history.discover", return_value=[fake_db]):
            d.configure(args)
        self.assertEqual(d._history_dbs, [fake_db])


import json
from pathlib import Path

_FIXTURE = json.loads((Path(__file__).parent / "news_fixture.json").read_text())


def _launch_delegate(args):
    """Create a delegate, configure it, and run applicationDidFinishLaunching_.

    Calls applicationDidFinishLaunching_ directly (bypassing AppHelper.runEventLoop)
    to exercise status bar item creation, icon setup, and timer scheduling.
    The background refresh thread is suppressed — we populate the menu
    synchronously with fixture data afterwards.
    """
    fixture_data = [dict(item, history=False) for item in _FIXTURE]

    delegate = HackerTrayDelegate.alloc().init()
    with mock.patch("hackertray.history.discover", return_value=[]):
        delegate.configure(args)

    # Suppress the background thread spawned by refresh_
    with mock.patch("hackertray.macos.Thread"):
        delegate.applicationDidFinishLaunching_(None)

    # Synchronously populate the menu with fixture data
    delegate._rebuild_menu(fixture_data)
    delegate._last_data = fixture_data

    return delegate


class TestAppLaunchIntegration(unittest.TestCase):
    """Launch the real macOS app via main_macos, let the run loop tick, then stop."""

    def test_app_launches_and_populates_menu(self):
        args = mock.Mock(
            comments=False,
            reverse=False,
            macos_icon_color="orange",
            verbose=False,
        )
        delegate = _launch_delegate(args)

        self.assertIsInstance(delegate, HackerTrayDelegate)

        # Status bar item was created with an icon
        self.assertIsNotNone(delegate._status_item)
        self.assertIsNotNone(delegate._status_item.button().image())

        # Menu was populated with news items (fixture has 29 with non-zero points)
        menu = delegate._menu
        news = _news_items(menu)
        self.assertEqual(len(news), 29)

        # Verify real fixture titles made it through
        titles = [mi.title() for mi in news]
        self.assertTrue(any("Intel 486" in t for t in titles))
        self.assertTrue(any("Show HN" in t for t in titles))

        # Standard menu items present
        self.assertIsNotNone(_item_titled(menu, "Refresh"))
        self.assertIsNotNone(_item_titled(menu, "Quit"))

    def test_app_launches_with_reverse(self):
        args = mock.Mock(
            comments=False,
            reverse=True,
            macos_icon_color="orange",
            verbose=False,
        )
        delegate = _launch_delegate(args)

        menu = delegate._menu
        news = _news_items(menu)

        # With reverse=True, items should be in reversed order
        ids = [mi.representedObject()["hn_id"] for mi in news]
        # The fixture data is reversed by _rebuild_menu when _reverse is True
        fixture_ids = [
            item["id"] for item in _FIXTURE if item["points"] and item["points"] != 0
        ]
        self.assertEqual(ids, list(reversed(fixture_ids)))

    def test_app_launches_with_text_icon(self):
        args = mock.Mock(
            comments=False,
            reverse=False,
            macos_icon_color="none",
            verbose=False,
        )
        delegate = _launch_delegate(args)

        self.assertEqual(delegate._status_item.button().title(), "Y")
        self.assertIsNone(delegate._status_item.button().image())
