#!/usr/bin/env python

import os
import urllib.error
import subprocess
import importlib
import importlib.resources

if(os.environ.get('CI') != 'true'):
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk,GLib
    import webbrowser
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3 as AppIndicator

import json
import argparse
from os.path import expanduser
import signal

from .hackernews import HackerNews
from .chrome import Chrome
from .firefox import Firefox
from .version import Version


class HackerNewsApp:
    HN_URL_PREFIX = "https://news.ycombinator.com/item?id="
    UPDATE_URL = "https://github.com/captn3m0/hackertray#upgrade"
    ABOUT_URL = "https://github.com/captn3m0/hackertray"

    def __init__(self, args):
        # Load the database
        home = expanduser("~")
        with open(home + '/.hackertray.json', 'a+') as content_file:
            content_file.seek(0)
            content = content_file.read()
            try:
                self.db = set(json.loads(content))
            except ValueError:
                self.db = set()

        # create an indicator applet
        self.ind = AppIndicator.Indicator.new("Hacker Tray", "hacker-tray", AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.ind.set_icon_theme_path(self._icon_theme_path())
        icon_name = "hacker-tray-light" if self._is_light_theme() else "hacker-tray"
        self.ind.set_icon(icon_name)

        # create a menu
        self.menu = Gtk.Menu()

        self.commentState = args.comments
        self.reverse = args.reverse
        self.chrome_data_directory = args.chrome

        # Resolve firefox: None = not requested, "auto" = detect, else = specific path
        self.firefox_explicit = args.firefox is not None and args.firefox != "auto"
        if args.firefox == "auto":
            self.firefox_data_directory = Firefox.default_firefox_profile_path()
        else:
            self.firefox_data_directory = args.firefox

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

        # Only show Firefox toggle if --firefox was unset or "auto"
        if not self.firefox_explicit:
            btnFirefox = Gtk.CheckMenuItem.new_with_label("Detect Firefox read items")
            btnFirefox.set_active(self.firefox_data_directory is not None)
            btnFirefox.connect("toggled", self.toggleFirefox)
            settingsMenu.append(btnFirefox)
            btnFirefox.show()

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
            btnUpdate.connect('activate', self.showUpdate)
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

    def toggleFirefox(self, widget):
        if widget.get_active():
            try:
                self.firefox_data_directory = Firefox.default_firefox_profile_path()
            except RuntimeError:
                print("[+] Could not find Firefox profile")
                widget.set_active(False)
                return
        else:
            self.firefox_data_directory = None

    def showUpdate(self, widget):
        """Handle the update button"""
        webbrowser.open(HackerNewsApp.UPDATE_URL)
        # Remove the update button once clicked
        self.menu.remove(widget)

    def showAbout(self, widget):
        """Handle the about btn"""
        webbrowser.open(HackerNewsApp.ABOUT_URL)

    # ToDo: Handle keyboard interrupt properly
    def quit(self, widget, data=None):
        """ Handler for the quit button"""
        l = list(self.db)[-200:]
        home = expanduser("~")

        with open(home + '/.hackertray.json', 'w+') as file:
            file.write(json.dumps(l))

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
            widget.signal_id = widget.connect('activate', self.open)

        self.db.add(widget.item_id)
        webbrowser.open(widget.url)

        # TODO: Add support for Shift+Click or Right Click
        # to do the opposite of the current commentState setting
        if self.commentState:
            webbrowser.open(self.HN_URL_PREFIX + str(widget.hn_id))

    def addItem(self, item):
        """Adds an item to the menu"""
        # This is in the case of YC Job Postings, which we skip
        if item['points'] == 0 or item['points'] is None:
            return

        points = str(item['points']).zfill(3) + "/" + str(item['comments_count']).zfill(3)

        i = Gtk.CheckMenuItem.new_with_label(label="(" + points + ")"+item['title'])
        label = i.get_child()
        label.set_markup("<tt>" + points + "</tt> <span>"+item['title']+"</span>".format(points=points, title=item['title']))
        label.set_selectable(False)

        visited = item['history'] or item['id'] in self.db
        print(f"[ui] {'visited' if visited else 'unvisited'}: {item['url']}")

        i.url = item['url']
        tooltip = "{url}\nPosted by {user} {timeago}".format(url=item['url'], user=item['user'], timeago=item['time_ago'])
        i.set_tooltip_text(tooltip)
        i.hn_id = item['id']
        i.item_id = item['id']
        i.set_active(visited)
        i.signal_id = i.connect('activate', self.open)
        if self.reverse:
            self.menu.append(i)
        else:
            self.menu.prepend(i)
        i.show()

    def refresh(self, widget=None, no_timer=False):
        """Refreshes the menu """
        try:
            # Create an array of 20 false to denote matches in History
            searchResults = [False]*20
            data = list(reversed(HackerNews.getHomePage()[0:20]))
            urls = [item['url'] for item in data]
            if self.chrome_data_directory:
                searchResults = self.mergeBoolArray(searchResults, Chrome.search(urls, self.chrome_data_directory))

            if self.firefox_data_directory:
                searchResults = self.mergeBoolArray(searchResults, Firefox.search(urls, self.firefox_data_directory))

            # Remove all the current stories
            for i in self.menu.get_children():
                if hasattr(i, 'url'):
                    self.menu.remove(i)

            # Add back all the refreshed news
            for index, item in enumerate(data):
                item['history'] = searchResults[index]
                if item['url'].startswith('item?id='):
                    item['url'] = "https://news.ycombinator.com/" + item['url']

                self.addItem(item)
        # Catch network errors
        except urllib.error.URLError as e:
            print("[+] There was an error in fetching news items")
        finally:
            # Call every 10 minutes
            if not no_timer:
                GLib.timeout_add(10 * 30 * 1000, self.refresh)

    # Merges two boolean arrays, using OR operation against each pair
    def mergeBoolArray(self, original, patch):
        for index, var in enumerate(original):
            original[index] = original[index] or patch[index]
        return original

    @staticmethod
    def _icon_theme_path():
        """Return the icon data dir as a host-accessible path.

        AppIndicator sends this path over D-Bus to the tray host, which runs
        outside the Flatpak sandbox. Inside a Flatpak, /app/ paths are not
        accessible from the host, so we translate via /.flatpak-info."""
        data_dir = str(importlib.resources.files('hackertray.data'))
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


def main():
    parser = argparse.ArgumentParser(description='Hacker News in your System Tray')
    parser.add_argument('-v', '--version', action='version', version=Version.current())
    parser.add_argument('-c', '--comments', dest='comments', default=False, action='store_true', help="Load the HN comments link for the article as well")
    parser.add_argument('--chrome', dest='chrome', help="Specify a Google Chrome Profile directory to use for matching chrome history")
    parser.add_argument('--firefox', dest='firefox', help="Specify a Firefox Profile directory to use for matching firefox history. Pass auto to automatically pick the default profile")
    parser.add_argument('-r', '--reverse', dest='reverse', default=False, action='store_true', help="Reverse the order of items. Use if your status bar is at the bottom of the screen")
    args = parser.parse_args()
    indicator = HackerNewsApp(args)
    indicator.run()
