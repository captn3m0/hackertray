This file will only list released and supported versions, usually skipping over very minor updates.

Unreleased
==========

4.0.2
=====

* Adds a --reverse flag for users with bar at the bottom of their screen
* Uses markup to keep points in fixed-width, so titles are more readable
* Removes the buggy hover-out behaviour (non-appindicator). You now need to click elsewhere to close the menu

4.0.1
=====

* Changes "Show Comments" entry to a radio menu item

4.0.0
=====

* Adds support for --firefox auto, picks the default firefox profile automatically
* Upgrades to Python 3.0. Python 2 is no longer supported
* Switches from PyGtk to PyGObject.
* AppIndicator is no longer supported, because it is Python 2 only
* Removed all MixPanel tracking.

3.0.0
=====

* Oct 3, 2014
* Major release.
* Firefox support behind `--firefox` flag
* Analytics support. Can be disabled using `--dnt` flag
* Hovering now shows url, timestamp, and uploader nick

2.3.2
=====

* Sep 27, 2014
* Adds proxy support


2.2.0
=====

* Adds support for using chrome history behind the `--chrome` flag.
