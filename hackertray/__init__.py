#!/usr/bin/env python

import os
import requests
import subprocess

if(os.environ.get('TRAVIS') != 'true'):
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk,GLib
    import webbrowser

    try:
        import appindicator
    except ImportError:
        from . import appindicator_replacement as appindicator

    from .appindicator_replacement import get_icon_filename

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
        self.ind = appindicator.Indicator("Hacker Tray", "hacker-tray", appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_icon(get_icon_filename("hacker-tray.png"))

        # create a menu
        self.menu = Gtk.Menu()

        # The default state is false, and it toggles when you click on it
        self.commentState = args.comments

        # create items for the menu - refresh, quit and a separator
        menuSeparator = Gtk.SeparatorMenuItem()
        menuSeparator.show()
        self.menu.append(menuSeparator)

        btnComments = Gtk.CheckMenuItem("Show Comments")
        btnComments.show()
        btnComments.set_active(args.comments)
        btnComments.set_draw_as_radio(True)
        btnComments.connect("activate", self.toggleComments)
        self.menu.append(btnComments)

        btnAbout = Gtk.MenuItem("About")
        btnAbout.show()
        btnAbout.connect("activate", self.showAbout)
        self.menu.append(btnAbout)

        btnRefresh = Gtk.MenuItem("Refresh")
        btnRefresh.show()
        # the last parameter is for not running the timer
        btnRefresh.connect("activate", self.refresh, True, args.chrome)
        self.menu.append(btnRefresh)

        if Version.new_available():
            btnUpdate = Gtk.MenuItem("New Update Available")
            btnUpdate.show()
            btnUpdate.connect('activate', self.showUpdate)
            self.menu.append(btnUpdate)

        btnQuit = Gtk.MenuItem("Quit")
        btnQuit.show()
        btnQuit.connect("activate", self.quit)
        self.menu.append(btnQuit)
        self.menu.show()
        self.ind.set_menu(self.menu)

        if args.firefox == "auto":
            args.firefox = Firefox.default_firefox_profile_path()
        self.refresh(chrome_data_directory=args.chrome, firefox_data_directory=args.firefox)

    def toggleComments(self, widget):
        """Whether comments page is opened or not"""
        self.commentState = not self.commentState

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
        l = list(self.db)
        home = expanduser("~")

        # truncate the file
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

        i = Gtk.CheckMenuItem(
            "(" + str(item['points']).zfill(3) + "/" + str(item['comments_count']).zfill(3) + ")    " + item['title'])

        visited = item['history'] or item['id'] in self.db

        i.set_active(visited)
        i.url = item['url']
        tooltip = "{url}\nPosted by {user} {timeago}".format(url=item['url'], user=item['user'], timeago=item['time_ago'])
        i.set_tooltip_text(tooltip)
        i.signal_id = i.connect('activate', self.open)
        i.hn_id = item['id']
        i.item_id = item['id']
        self.menu.prepend(i)
        i.show()

    def refresh(self, widget=None, no_timer=False, chrome_data_directory=None, firefox_data_directory=None):
        """Refreshes the menu """
        try:
            # Create an array of 20 false to denote matches in History
            searchResults = [False]*20
            data = list(reversed(HackerNews.getHomePage()[0:20]))
            urls = [item['url'] for item in data]
            if(chrome_data_directory):
                searchResults = self.mergeBoolArray(searchResults, Chrome.search(urls, chrome_data_directory))

            if(firefox_data_directory):
                searchResults = self.mergeBoolArray(searchResults, Firefox.search(urls, firefox_data_directory))

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
        except requests.exceptions.RequestException as e:
            print("[+] There was an error in fetching news items")
        finally:
            # Call every 10 minutes
            if not no_timer:
                GLib.timeout_add(10 * 30 * 1000, self.refresh, widget, no_timer, chrome_data_directory)

    # Merges two boolean arrays, using OR operation against each pair
    def mergeBoolArray(self, original, patch):
        for index, var in enumerate(original):
            original[index] = original[index] or patch[index]
        return original


def main():
    parser = argparse.ArgumentParser(description='Hacker News in your System Tray')
    parser.add_argument('-v', '--version', action='version', version=Version.current())
    parser.add_argument('-c', '--comments', dest='comments', action='store_true', help="Load the HN comments link for the article as well")
    parser.add_argument('--chrome', dest='chrome', help="Specify a Google Chrome Profile directory to use for matching chrome history")
    parser.add_argument('--firefox', dest='firefox', help="Specify a Firefox Profile directory to use for matching firefox history. Pass auto to automatically pick the default profile")
    parser.set_defaults(comments=False)
    parser.set_defaults(dnt=False)
    args = parser.parse_args()
    indicator = HackerNewsApp(args)
    indicator.run()
