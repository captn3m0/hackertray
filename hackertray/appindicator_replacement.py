#=========================
#
# AppIndicator for GTK
#  drop-in replacement
#
#    Copyright 2010
#     Nathan Osman
#
#=========================

# We require PyGTK
from gi.repository import Gtk,GLib

# We also need os and sys
import os

from pkg_resources import resource_filename

# Types
CATEGORY_APPLICATION_STATUS = 0

# Status
STATUS_ACTIVE = 0
STATUS_ATTENTION = 1

# Locations to search for the given icon


def get_icon_filename(icon_name):
    # Determine where the icon is
    return os.path.abspath(resource_filename('hackertray.data', 'hacker-tray.png'))


# The main class
class Indicator:
    # Constructor

    def __init__(self, unknown, icon, category):
        # Store the settings
        self.inactive_icon = get_icon_filename(icon)
        self.active_icon = ""  # Blank until the user calls set_attention_icon

        # Create the status icon
        self.icon = Gtk.StatusIcon()

        # Initialize to the default icon
        self.icon.set_from_file(self.inactive_icon)

        # Set the rest of the vars
        self.menu = None    # We have no menu yet

    def set_menu(self, menu):
        # Save a copy of the menu
        self.menu = menu

        # Now attach the icon's signal
        # to the menu so that it becomes displayed
        # whenever the user clicks it
        self.icon.connect("activate", self.show_menu)

    def set_status(self, status):
        # Status defines whether the active or inactive
        # icon should be displayed.
        if status == STATUS_ACTIVE:
            self.icon.set_from_file(self.inactive_icon)
        else:
            self.icon.set_from_file(self.active_icon)

    def set_label(self, label):
        self.icon.set_title(label)
        return

    def set_icon(self, icon):
        # Set the new icon
        self.icon.set_from_file(get_icon_filename(icon))

    def set_attention_icon(self, icon):
        # Set the icon filename as the attention icon
        self.active_icon = get_icon_filename(icon)

    def show_menu(self, widget):
        # Show the menu
        self.menu.popup(None, None, None, 0, 0, Gtk.get_current_event_time())

    def hide_menu(self):
        self.menu.popdown()
