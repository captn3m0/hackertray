#!/usr/bin/env python

import pygtk

pygtk.require('2.0')
import gtk

import webbrowser
import json
import argparse
from os.path import expanduser
import signal

try:
    import appindicator
except ImportError:
    import appindicator_replacement as appindicator

from appindicator_replacement import get_icon_filename

##This is to get --version to work
try:
    import pkg_resources

    __version = pkg_resources.require("hackertray")[0].version
except ImportError:
    __version = "Can't read version number."

from hackernews import HackerNews


class HackerNewsApp:
    HN_URL_PREFIX = "https://news.ycombinator.com/item?id="

    def __init__(self, comments):
        #Load the database
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
        self.menu = gtk.Menu()

        #The default state is false, and it toggles when you click on it
        self.commentState = comments

        # create items for the menu - refresh, quit and a separator
        menuSeparator = gtk.SeparatorMenuItem()
        menuSeparator.show()
        self.menu.append(menuSeparator)

        btnComments = gtk.CheckMenuItem("Show Comments")
        btnComments.show()
        btnComments.set_active(comments)
        btnComments.connect("activate", self.toggleComments)
        self.menu.append(btnComments)

        btnAbout = gtk.MenuItem("About")
        btnAbout.show()
        btnAbout.connect("activate", self.showAbout)
        self.menu.append(btnAbout)

        btnRefresh = gtk.MenuItem("Refresh")
        btnRefresh.show()
        #the last parameter is for not running the timer
        btnRefresh.connect("activate", self.refresh, True)
        self.menu.append(btnRefresh)

        btnQuit = gtk.MenuItem("Quit")
        btnQuit.show()
        btnQuit.connect("activate", self.quit)
        self.menu.append(btnQuit)

        self.menu.show()

        self.ind.set_menu(self.menu)
        self.refresh()

    def toggleComments(self, widget):
        """Whether comments page is opened or not"""
        self.commentState = not self.commentState

    def showAbout(self, widget):
        """Handle the about btn"""
        webbrowser.open("https://github.com/captn3m0/hackertray/")

    #ToDo: Handle keyboard interrupt properly
    def quit(self, widget, data=None):
        """ Handler for the quit button"""
        l = list(self.db)
        home = expanduser("~")

        #truncate the file
        with open(home + '/.hackertray.json', 'w+') as file:
            file.write(json.dumps(l))

        gtk.main_quit()

    def run(self):
        signal.signal(signal.SIGINT, self.quit)
        gtk.main()
        return 0

    def open(self, widget, event=None, data=None):
        """Opens the link in the web browser"""
        #We disconnect and reconnect the event in case we have
        #to set it to active and we don't want the signal to be processed
        if not widget.get_active():
            widget.disconnect(widget.signal_id)
            widget.set_active(True)
            widget.signal_id = widget.connect('activate', self.open)

        self.db.add(widget.item_id)
        webbrowser.open(widget.url)

        if self.commentState:
            webbrowser.open(self.HN_URL_PREFIX + widget.hn_id)

    def addItem(self, item):
        """Adds an item to the menu"""
        #This is in the case of YC Job Postings, which we skip
        if item['points'] == 0 or item['points'] is None:
            return

        i = gtk.CheckMenuItem(
            "(" + str(item['points']).zfill(3) + "/" + str(item['comments_count']).zfill(3) + ")    " + item['title'])

        i.set_active(item['id'] in self.db)
        i.url = item['url']
        i.signal_id = i.connect('activate', self.open)
        i.hn_id = item['id']
        i.item_id = item['id']
        self.menu.prepend(i)
        i.show()

    def refresh(self, widget=None, no_timer=False):
        """Refreshes the menu """
        data = reversed(HackerNews.getHomePage()[0:20])

        #Remove all the current stories
        for i in self.menu.get_children():
            if hasattr(i, 'url'):
                self.menu.remove(i)

        #Add back all the refreshed news
        for i in data:
            self.addItem(i)

        #Call every 5 minutes
        if not no_timer:
            gtk.timeout_add(10 * 60 * 1000, self.refresh)


def main():
    parser = argparse.ArgumentParser(description='Hacker News in your System Tray')
    parser.add_argument('-v','--version', action='version', version=__version)
    parser.add_argument('-c','--comments', dest='comments',action='store_true', help="Load the HN comments link for the article as well")
    parser.set_defaults(comments=False)
    args = parser.parse_args()
    indicator = HackerNewsApp(args.comments)
    indicator.run()
