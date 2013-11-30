#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk

import requests
import webbrowser
import json

from os.path import expanduser

try:
    import appindicator
except ImportError:
    import appindicator_replacement as appindicator

from hackernews import HackerNews

class HackerNewsApp:
	def __init__(self):
		#Load the database
		home = expanduser("~")
		with open(home+'/.hackertray.json', 'a+') as content_file:
			content_file.seek(0)
			content = content_file.read()
			try:
				self.db = set(json.loads(content))
			except:
				self.db = set()

		# create an indicator applet
		self.ind = appindicator.Indicator ("Hacker Tray", "hacker-tray", appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status (appindicator.STATUS_ACTIVE)
		self.ind.set_label("Y")

		# create a menu
		self.menu = gtk.Menu()

		# create items for the menu - refresh, quit and a separator
		menuSeparator = gtk.SeparatorMenuItem()
		menuSeparator.show()
		self.menu.append(menuSeparator)
		
		#open hacker news 
		btnHnLink = gtk.MenuItem("Hacker News")
                btnHnLink.show()
                btnHnLink.connect("activate", self.showHnLink)
                self.menu.append(btnHnLink)


		btnAbout = gtk.MenuItem("About")
		btnAbout.show()
		btnAbout.connect("activate", self.showAbout)
		self.menu.append(btnAbout)

		btnRefresh = gtk.MenuItem("Refresh")
		btnRefresh.show()
		btnRefresh.connect("activate", self.refresh, True) #the last parameter is for not running the timer
		self.menu.append(btnRefresh)

		btnQuit = gtk.MenuItem("Quit")
		btnQuit.show()
		btnQuit.connect("activate", self.quit)
		self.menu.append(btnQuit)

		self.menu.show()

		self.ind.set_menu(self.menu)
		self.refresh()

	'''Handle the about btn'''
	def showAbout(self, widget):
		webbrowser.open("https://github.com/captn3m0/hackertray/")

	def showHnLink(self, widget):
                webbrowser.open("https://news.ycombinator.com/")

	''' Handler for the quit button'''
	#ToDo: Handle keyboard interrupt properly
	def quit(self, widget, data=None):
		l=list(self.db)
		home = expanduser("~")
		#truncate the file
		with open(home+'/.hackertray.json', 'w+') as file:
			file.write(json.dumps(l))
		gtk.main_quit()

	def run(self):
		gtk.main()
		return 0

	'''Opens the link in the web browser'''
	def open(self, widget, event=None, data=None):
		#We disconnect and reconnect the event in case we have
		#to set it to active and we don't want the signal to be processed
		if(widget.get_active() == False):
			widget.disconnect(widget.signal_id)
			widget.set_active(True)
			widget.signal_id = widget.connect('activate', self.open)
		self.db.add(widget.item_id)
		webbrowser.open(widget.url)

	'''Adds an item to the menu'''
	def addItem(self, item):
		if(item['points'] == 0 or item['points'] == None): #This is in the case of YC Job Postings, which we skip
			return
		i = gtk.CheckMenuItem("("+str(item['points']).zfill(3)+"/"+str(item['comments_count']).zfill(3)+")    "+item['title'])
		i.set_active(item['id'] in self.db)
		i.url = item['url']
		i.signal_id = i.connect('activate', self.open)
		i.item_id = item['id']
		self.menu.prepend(i)
		i.show()

	'''Refreshes the menu '''
	def refresh(self, widget=None, no_timer=False):
		data = reversed(HackerNews.getHomePage()[0:20]);
		#Remove all the current stories
		for i in self.menu.get_children():
			if(hasattr(i,'url')):
				self.menu.remove(i)
		#Add back all the refreshed news
		for i in data:
			self.addItem(i)
		#Call every 5 minutes
		if no_timer==False:
			gtk.timeout_add(10*60*1000, self.refresh)

def main():
	indicator = HackerNewsApp()
	indicator.run()
