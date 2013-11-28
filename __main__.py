#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk

import requests
import webbrowser

try:
    import appindicator
except ImportError:
    import appindicator_replacement as appindicator

class HackerNewsApp:
	def __init__(self):
		self.ind = appindicator.Indicator ("Hacker Tray", "hacker-tray", appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status (appindicator.STATUS_ACTIVE)
		self.ind.set_label("Y")

		# create a menu
		self.menu = gtk.Menu()

		# create items for the menu - labels, checkboxes, radio buttons and images are supported:
		menuSeparator = gtk.SeparatorMenuItem()
		menuSeparator.show()
		self.menu.append(menuSeparator)

		btnRefresh = gtk.MenuItem("Refresh")
		btnRefresh.show()
		btnRefresh.connect("activate", self.refresh)
		self.menu.append(btnRefresh)

		btnQuit = gtk.MenuItem("Quit")
		btnQuit.show()
		btnQuit.connect("activate", self.quit)
		self.menu.append(btnQuit)

		self.menu.show()

		self.ind.set_menu(self.menu)
		self.refresh()

	def quit(self, widget, data=None):
		gtk.main_quit()

	def open(self, widget, event=None, data=None):
		#We disconnect and reconnect the event in case we have
		#to set it to active and we don't want the signal to be processed
		if(widget.get_active() == False):
			widget.disconnect(widget.signal_id)
			widget.set_active(True)
			widget.signal_id = widget.connect('activate', self.open)
		webbrowser.open(widget.url)

	def addItem(self, item):
		if(item['points'] == 0 or item['points'] == None): #This is in the case of YC Job Postings, which we skip
			return
		i = gtk.CheckMenuItem("("+str(item['points']).zfill(3)+"/"+str(item['comments_count']).zfill(3)+")    "+item['title'])
		i.url = item['url']
		i.signal_id = i.connect('activate', self.open)
		self.menu.prepend(i)
		i.show()

	def refresh(self, widget=None, data=None):
		self.data = reversed(getHomePage()[0:15]);
		for i in self.menu.get_children():
			if(hasattr(i,'url')):
				self.menu.remove(i)
		for i in self.data:
			self.addItem(i)


def getHomePage():
	r = requests.get('https://node-hnapi.herokuapp.com/news')
	return r.json()

def main():
	gtk.main()
	return 0

if __name__ == "__main__":
	indicator = HackerNewsApp()
	main()