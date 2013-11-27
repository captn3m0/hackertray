#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import appindicator
import requests
import webbrowser

class HackerNewsApp:
	def __init__(self):
		self.ind = appindicator.Indicator ("Hacker Tray", "hacker-tray", appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status (appindicator.STATUS_ACTIVE)
		self.ind.set_label("Y")

		# create a menu
		self.menu = gtk.Menu()

		# create items for the menu - labels, checkboxes, radio buttons and images are supported:
		btnRefresh = gtk.MenuItem("Refresh This")
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

	def open(self, widget, data=None):
		webbrowser.open(widget.url)

	def addItem(self, item):
		i = gtk.CheckMenuItem("("+str(item['points']).zfill(3)+"/"+str(item['comments_count']).zfill(3)+")    "+item['title'])
		i.url = item['url']
		i.connect('activate', self.open)
		self.menu.prepend(i)
		i.show()

	def refresh(self, widget=None, data=None):
		self.data = reversed(getHomePage()[0:15]);
		for i in self.menu.get_children():
			if(i.__class__.__name__=="CheckMenuItem"):
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