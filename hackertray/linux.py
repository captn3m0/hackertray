#!/usr/bin/env python
"""Linux GTK system tray app for HackerTray."""

import logging
import signal
import urllib.error
import webbrowser

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3 as AppIndicator

import importlib
import importlib.resources
import os
import configparser

from .hackernews import HackerNews
from .version import Version

logger = logging.getLogger(__name__)


class HackerNewsApp:
    HN_URL_PREFIX = "https://news.ycombinator.com/item?id="
    UPDATE_URL = "https://github.com/captn3m0/hackertray#upgrade"
    ABOUT_URL = "https://github.com/captn3m0/hackertray"

    def __init__(self, args):
        # create an indicator applet
        self.ind = AppIndicator.Indicator.new(
            "Hacker Tray",
            "hacker-tray",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS,
        )
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.ind.set_icon_theme_path(self._icon_theme_path())
        icon_name = "hacker-tray-light" if self._is_light_theme() else "hacker-tray"
        self.ind.set_icon(icon_name)

        # create a menu
        self.menu = Gtk.Menu()

        self.commentState = args.comments
        self.reverse = args.reverse

        # Discover browser history databases
        from .history import discover

        self._history_dbs = discover()

        # create items for the menu - separator, settings, about, refresh, quit
        menuSeparator = Gtk.SeparatorMenuItem()
        menuSeparator.show()
        self.add(menuSeparator)

        # Settings submenu
        settingsItem = Gtk.MenuItem.new_with_label("Settings")
        settingsMenu = Gtk.Menu()
        settingsItem.set_submenu(settingsMenu)

        btnComments = Gtk.CheckMenuItem.new_with_label("Open Comments")
        btnComments.set_active(args.comments)
        btnComments.connect("toggled", self.toggleComments)
        settingsMenu.append(btnComments)
        btnComments.show()

        btnReverse = Gtk.CheckMenuItem.new_with_label("Reverse Ordering")
        btnReverse.set_active(args.reverse)
        btnReverse.connect("toggled", self.toggleReverse)
        settingsMenu.append(btnReverse)
        btnReverse.show()

        self.add(settingsItem)
        settingsItem.show()

        btnAbout = Gtk.MenuItem.new_with_label("About")
        btnAbout.show()
        btnAbout.connect("activate", self.showAbout)
        self.add(btnAbout)

        btnRefresh = Gtk.MenuItem.new_with_label("Refresh")
        btnRefresh.show()
        btnRefresh.connect("activate", self.refresh, True)
        self.add(btnRefresh)

        if Version.new_available():
            btnUpdate = Gtk.MenuItem.new_with_label("New Update Available")
            btnUpdate.show()
            btnUpdate.connect("activate", self.showUpdate)
            self.add(btnUpdate)

        btnQuit = Gtk.MenuItem.new_with_label("Quit")
        btnQuit.show()
        btnQuit.connect("activate", self.quit)
        self.add(btnQuit)
        self.menu.show()
        self.ind.set_menu(self.menu)

        self.refresh()

    def add(self, item):
        if self.reverse:
            self.menu.prepend(item)
        else:
            self.menu.append(item)

    def toggleComments(self, widget):
        """Whether comments page is opened or not"""
        self.commentState = widget.get_active()

    def toggleReverse(self, widget):
        self.reverse = widget.get_active()

    def showUpdate(self, widget):
        """Handle the update button"""
        webbrowser.open(HackerNewsApp.UPDATE_URL)
        # Remove the update button once clicked
        self.menu.remove(widget)

    def showAbout(self, widget):
        """Handle the about btn"""
        webbrowser.open(HackerNewsApp.ABOUT_URL)

    def quit(self, widget, data=None):
        """Handler for the quit button"""
        Gtk.main_quit()

    def run(self):
        signal.signal(signal.SIGINT, self.quit)
        Gtk.main()
        return 0

    def open(self, widget, **args):
        """Opens the link in the web browser"""
        # We disconnect and reconnect the event in case we have
        # to set it to active and we don't want the signal to be processed
        if not widget.get_active():
            widget.disconnect(widget.signal_id)
            widget.set_active(True)
            widget.signal_id = widget.connect("activate", self.open)

        webbrowser.open(widget.url)

        # TODO: Add support for Shift+Click or Right Click
        # to do the opposite of the current commentState setting
        if self.commentState:
            webbrowser.open(self.HN_URL_PREFIX + str(widget.hn_id))

    def addItem(self, item):
        """Adds an item to the menu"""
        # This is in the case of YC Job Postings, which we skip
        if item["points"] == 0 or item["points"] is None:
            return

        points = (
            str(item["points"]).zfill(3) + "/" + str(item["comments_count"]).zfill(3)
        )

        i = Gtk.CheckMenuItem.new_with_label(label="(" + points + ")" + item["title"])
        label = i.get_child()
        label.set_markup(
            "<tt>"
            + points
            + "</tt> <span>"
            + item["title"]
            + "</span>".format(points=points, title=item["title"])
        )
        label.set_selectable(False)

        visited = item["history"]
        logger.debug("%s: %s", "visited" if visited else "unvisited", item["url"])

        i.url = item["url"]
        tooltip = "{url}\nPosted by {user} {timeago}".format(
            url=item["url"], user=item["user"], timeago=item["time_ago"]
        )
        i.set_tooltip_text(tooltip)
        i.hn_id = item["id"]
        i.item_id = item["id"]
        i.set_active(visited)
        i.signal_id = i.connect("activate", self.open)
        if self.reverse:
            self.menu.append(i)
        else:
            self.menu.prepend(i)
        i.show()

    def refresh(self, widget=None, no_timer=False):
        """Refreshes the menu"""
        try:
            data = list(reversed(HackerNews.getHomePage()[0:20]))
            urls = [item["url"] for item in data]

            # Search browser history
            from .history import search as history_search

            visited_urls = history_search(urls, self._history_dbs)

            # Remove all the current stories
            for i in self.menu.get_children():
                if hasattr(i, "url"):
                    self.menu.remove(i)

            # Add back all the refreshed news
            for item in data:
                item["history"] = item["url"] in visited_urls
                if item["url"].startswith("item?id="):
                    item["url"] = "https://news.ycombinator.com/" + item["url"]

                self.addItem(item)
        # Catch network errors
        except urllib.error.URLError as e:
            print("[+] There was an error in fetching news items")
        finally:
            # Call every 10 minutes
            if not no_timer:
                GLib.timeout_add(10 * 30 * 1000, self.refresh)

    @staticmethod
    def _icon_theme_path():
        """Return the icon data dir as a host-accessible path.

        AppIndicator sends this path over D-Bus to the tray host, which runs
        outside the Flatpak sandbox. Inside a Flatpak, /app/ paths are not
        accessible from the host, so we translate via /.flatpak-info."""
        data_dir = str(importlib.resources.files("hackertray.data"))
        if os.path.exists("/.flatpak-info"):
            import configparser

            info = configparser.ConfigParser()
            info.read("/.flatpak-info")
            app_path = info.get("Instance", "app-path")
            data_dir = app_path + data_dir.removeprefix("/app")
        return data_dir

    @staticmethod
    def _is_light_theme():
        settings = Gtk.Settings.get_default()
        if settings and settings.get_property("gtk-application-prefer-dark-theme"):
            return False
