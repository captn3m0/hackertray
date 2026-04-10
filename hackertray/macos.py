#!/usr/bin/env python
"""Native macOS status bar app for HackerTray using pyobjc."""

import logging
import webbrowser
import signal
import urllib.error
from threading import Thread

logger = logging.getLogger(__name__)

import objc
from AppKit import (
    NSApplication,
    NSStatusBar,
    NSMenu,
    NSMenuItem,
    NSFont,
    NSFontAttributeName,
    NSForegroundColorAttributeName,
    NSBackgroundColorAttributeName,
    NSColor,
    NSImage,
    NSMutableAttributedString,
    NSBezierPath,
    NSTimer,
    NSVariableStatusItemLength,
    NSApp,
    NSOnState,
    NSOffState,
    NSApplicationActivationPolicyAccessory,
)
from Foundation import (
    NSObject,
    NSMakeRange,
    NSMakeRect,
    NSMakeSize,
    NSMakePoint,
    NSDictionary,
)
from PyObjCTools import AppHelper

from .hackernews import HackerNews
from .version import Version


HN_URL_PREFIX = "https://news.ycombinator.com/item?id="
UPDATE_URL = "https://github.com/captn3m0/hackertray#upgrade"
ABOUT_URL = "https://github.com/captn3m0/hackertray"


class HackerTrayDelegate(NSObject):
    def init(self):
        self = objc.super(HackerTrayDelegate, self).init()
        if self is None:
            return None
        self._comment_state = False
        self._reverse = False
        self._history_dbs = []
        self._pending_data = None
        self._last_data = None  # last fetched data for live redraws
        return self

    @objc.python_method
    def configure(self, args):
        from . import history

        self._comment_state = args.comments
        self._reverse = args.reverse
        self._icon_color = getattr(args, "macos_icon_color", "orange") or "orange"

        # Discover all browser history databases
        self._history_dbs = history.discover()

    def applicationDidFinishLaunching_(self, notification):
        # Status bar item
        self._status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        if self._icon_color == "none":
            self._status_item.setTitle_("Y")
            self._status_item.button().setFont_(NSFont.boldSystemFontOfSize_(14.0))
        else:
            self._status_item.button().setImage_(self._make_yc_icon())
        logger.debug("Status bar item created (icon_color=%s)", self._icon_color)

        # Menu
        self._menu = NSMenu.alloc().init()
        self._menu.setAutoenablesItems_(False)

        # Add a loading item so the menu isn't empty
        loading = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Loading...", None, ""
        )
        loading.setEnabled_(False)
        self._menu.addItem_(loading)

        self._status_item.setMenu_(self._menu)

        # Kick off first refresh
        self.refresh_(None)

        # Refresh every 5 minutes
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            300.0, self, b"refresh:", None, True
        )

        # Timer to allow Python signal handling (Ctrl+C)
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            1.0, self, b"signalCheck:", None, True
        )

    def signalCheck_(self, timer):
        """No-op timer that gives Python a chance to handle signals."""
        pass

    def refresh_(self, timer):
        """Refresh news items in a background thread."""
        logger.debug("refresh_ called, spawning background fetch thread")
        Thread(target=self._fetch_and_update, daemon=True).start()

    @objc.python_method
    def _fetch_and_update(self):
        try:
            logger.debug("Fetching HN homepage...")
            data = list(reversed(HackerNews.getHomePage()[0:20]))
            logger.debug("Got %d items from HN", len(data))
            urls = [item["url"] for item in data]

            # Search browser history
            from . import history

            visited_urls = history.search(urls, self._history_dbs)
            logger.debug("Found %d visited URLs", len(visited_urls))

            for item in data:
                item["history"] = item["url"] in visited_urls
                if item["url"].startswith("item?id="):
                    item["url"] = "https://news.ycombinator.com/" + item["url"]

            # Stash data and poke the main thread
            self._pending_data = data
            logger.debug("Posting applyPendingData: to main thread")
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                b"applyPendingData:", None, False
            )
        except urllib.error.URLError as e:
            logger.error("URL error fetching news: %s", e)
        except Exception as e:
            logger.error("Error during refresh: %s", e, exc_info=True)

    def applyPendingData_(self, ignored):
        """Called on the main thread to rebuild the menu from _pending_data."""
        logger.debug("applyPendingData_ called on main thread")
        data = self._pending_data
        if data is None:
            logger.debug("No pending data, skipping")
            return
        self._pending_data = None
        self._last_data = data
        self._rebuild_menu(data)

    @objc.python_method
    def _rebuild_menu(self, data):
        logger.debug("_rebuild_menu: rebuilding with %d items", len(data))
        self._menu.removeAllItems()

        items_to_add = list(data)
        if self._reverse:
            items_to_add = list(reversed(items_to_add))

        for item in items_to_add:
            if item["points"] == 0 or item["points"] is None:
                continue
            mi = self._make_news_item(item)
            self._menu.addItem_(mi)

        # -- Separator --
        self._menu.addItem_(NSMenuItem.separatorItem())

        # Refresh
        refresh_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Refresh", b"refresh:", ""
        )
        refresh_item.setTarget_(self)
        self._menu.addItem_(refresh_item)

        # Settings submenu
        settings_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Settings", None, ""
        )
        settings_menu = NSMenu.alloc().init()
        settings_menu.setAutoenablesItems_(False)

        comments_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Open Comments", b"toggleComments:", ""
        )
        comments_item.setTarget_(self)
        comments_item.setState_(NSOnState if self._comment_state else NSOffState)
        settings_menu.addItem_(comments_item)

        reverse_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Reverse Ordering", b"toggleReverse:", ""
        )
        reverse_item.setTarget_(self)
        reverse_item.setState_(NSOnState if self._reverse else NSOffState)
        settings_menu.addItem_(reverse_item)

        settings_item.setSubmenu_(settings_menu)
        self._menu.addItem_(settings_item)

        # About
        about_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "About HackerTray", b"showAbout:", ""
        )
        about_item.setTarget_(self)
        self._menu.addItem_(about_item)

        # -- Separator + Quit --
        self._menu.addItem_(NSMenuItem.separatorItem())
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", b"quit:", ""
        )
        quit_item.setTarget_(self)
        self._menu.addItem_(quit_item)
        logger.debug(
            "_rebuild_menu: done, menu has %d items", self._menu.numberOfItems()
        )

    @objc.python_method
    def _make_news_item(self, item):
        """Create a styled menu item mimicking Hacker Bar's layout."""
        visited = item["history"]
        logger.debug("%s: %s", "visited" if visited else "unvisited", item["url"])

        points = str(item["points"]).zfill(3)
        comments = str(item["comments_count"]).zfill(3)
        title = item["title"]

        # Build attributed string: "123/456  Title"
        mono = NSFont.monospacedDigitSystemFontOfSize_weight_(13.0, 0.0)
        regular = NSFont.systemFontOfSize_(13.0)

        score_str = f"{points}/{comments}  "
        full_str = score_str + title

        attr_str = NSMutableAttributedString.alloc().initWithString_(full_str)
        attr_str.addAttribute_value_range_(
            NSFontAttributeName, mono, NSMakeRange(0, len(score_str))
        )
        attr_str.addAttribute_value_range_(
            NSForegroundColorAttributeName,
            NSColor.secondaryLabelColor(),
            NSMakeRange(0, len(score_str)),
        )
        # Gray background on comment count
        comment_start = len(points) + 1  # after "123/"
        attr_str.addAttribute_value_range_(
            NSBackgroundColorAttributeName,
            NSColor.colorWithSRGBRed_green_blue_alpha_(0.5, 0.5, 0.5, 0.15),
            NSMakeRange(comment_start, len(comments)),
        )

        title_start = len(score_str)
        attr_str.addAttribute_value_range_(
            NSFontAttributeName, regular, NSMakeRange(title_start, len(title))
        )

        # Orange background on "Show HN" tag
        show_hn_tag = "Show HN"
        if title.startswith("Show HN:"):
            attr_str.addAttribute_value_range_(
                NSBackgroundColorAttributeName,
                NSColor.colorWithSRGBRed_green_blue_alpha_(1.0, 0.6, 0.0, 0.15),
                NSMakeRange(title_start, len(show_hn_tag)),
            )

        mi = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            full_str, b"openLink:", ""
        )
        mi.setAttributedTitle_(attr_str)
        mi.setTarget_(self)

        tooltip = "{url}\nPosted by {user} {timeago}".format(
            url=item["url"], user=item.get("user", ""), timeago=item.get("time_ago", "")
        )
        mi.setToolTip_(tooltip)

        mi.setRepresentedObject_(
            {
                "url": item["url"],
                "hn_id": item["id"],
                "item_id": item["id"],
            }
        )

        if visited:
            mi.setState_(NSOnState)

        return mi

    def openLink_(self, sender):
        info = sender.representedObject()
        if info is None:
            return
        url = info["url"]
        item_id = info["item_id"]
        hn_id = info["hn_id"]

        webbrowser.open(url)

        if self._comment_state:
            webbrowser.open(HN_URL_PREFIX + str(hn_id))

        # Redraw to show visited checkmark
        if self._last_data is not None:
            self._rebuild_menu(self._last_data)

    def toggleComments_(self, sender):
        self._comment_state = not self._comment_state
        sender.setState_(NSOnState if self._comment_state else NSOffState)

    def toggleReverse_(self, sender):
        self._reverse = not self._reverse
        if self._last_data is not None:
            self._rebuild_menu(self._last_data)

    def showAbout_(self, sender):
        webbrowser.open(ABOUT_URL)

    def showUpdate_(self, sender):
        webbrowser.open(UPDATE_URL)

    def quit_(self, sender):
        AppHelper.stopEventLoop()

    @objc.python_method
    def _make_yc_icon(self):
        """Create a YC-style icon: colored rounded-rect with contrasting Y."""
        bg_colors = {
            "orange": (1.0, 0.4, 0.0),  # #FF6600
            "black": (0.0, 0.0, 0.0),
            "white": (1.0, 1.0, 1.0),
            "green": (0.0, 0.5, 0.0),
        }
        fg_colors = {
            "orange": NSColor.whiteColor(),
            "black": NSColor.whiteColor(),
            "white": NSColor.blackColor(),
            "green": NSColor.whiteColor(),
        }
        r, g, b = bg_colors[self._icon_color]
        bg = NSColor.colorWithSRGBRed_green_blue_alpha_(r, g, b, 1.0)
        fg = fg_colors[self._icon_color]

        size = 18.0
        img = NSImage.alloc().initWithSize_(NSMakeSize(size, size))
        img.lockFocus()

        bg.setFill()
        NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            NSMakeRect(0, 0, size, size), 3.0, 3.0
        ).fill()

        attrs = NSDictionary.dictionaryWithObjects_forKeys_(
            [NSFont.monospacedSystemFontOfSize_weight_(13.0, 0.0), fg],
            [NSFontAttributeName, NSForegroundColorAttributeName],
        )
        y_str = NSMutableAttributedString.alloc().initWithString_attributes_("Y", attrs)
        str_size = y_str.size()
        y_str.drawAtPoint_(
            NSMakePoint(
                (size - str_size.width) / 2.0,
                (size - str_size.height) / 2.0,
            )
        )

        img.unlockFocus()
        img.setTemplate_(False)
        return img


def main_macos(args):
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

    delegate = HackerTrayDelegate.alloc().init()
    delegate.configure(args)
    app.setDelegate_(delegate)

    # Ctrl+C handler
    def handle_sigint(*_):
        AppHelper.stopEventLoop()

    signal.signal(signal.SIGINT, handle_sigint)

    AppHelper.runEventLoop()
