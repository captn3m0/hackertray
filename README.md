HackerTray
==========

[![HackerTray on PyPi](https://pypip.in/v/hackertray/badge.png)](https://pypi.python.org/pypi/hackertray/)
[![HackerTray on PyPi](https://pypip.in/d/hackertray/badge.png)](https://pypi.python.org/pypi/hackertray/)
[![Build Status](https://travis-ci.org/captn3m0/hackertray.png)](https://travis-ci.org/captn3m0/hackertray)

HackerTray is a simple [Hacker News](https://news.ycombinator.com/) Linux application
that lets you view top HN stories in your System Tray. It relies on appindicator, so
it is not guaranteed to work on all systems. It also provides a Gtk StatusIcon fallback
in case AppIndicator is not available.

The inspiration for this came from [Hacker Bar](http://hackerbarapp.com), which is Mac-only.

##Screenshot

![HackerTray Screenshot in elementaryOS](http://i.imgur.com/63l3qXV.png)

##Installation
HackerTray is distributed as a python package. Do the following to install:

``` sh
sudo pip install hackertray
OR
sudo easy_install hackertray
OR
#Download Source and cd to it
sudo python setup.py install
```

After that, you can run `hackertray` from anywhere and it will run. You can
now add it to your OS dependent session autostart method. In Ubuntu, you can
access it via: 

1. System > Preferences > Sessions  
(OR)
2. System > Preferences > Startup Applications 

depending on your Ubuntu Version. Or put it in `~/.config/openbox/autostart` 
if you are running OpenBox. [Here](http://imgur.com/mnhIzDK) is how the 
configuration should look like in Ubuntu and its derivatives. 

###Upgrade
The latest stable version is [![the one on PyPi](https://pypip.in/v/hackertray/badge.png)](https://pypi.python.org/pypi/hackertray/)

You can check which version you have installed with `hackertray --version`.

To upgrade, run `pip install -U hackertray`. In some cases (Ubuntu), you might
need to clear the pip cache before upgrading:

`sudo rm -rf /tmp/pip-build-root/hackertray`

HackerTray will automatically check the latest version on startup, and inform you if there is an update available.

##Options
HackerTray accepts its various options via the command line. Run `hackertray -h` to see all options. Currently the following switches are supported:

1. `-c`: Enables comments support. Clicking on links will also open the comments page on HN. Can be switched off via the UI, but the setting is not remembered.
2. `--chrome PROFILE_PATH`: Specifying a profile path to a chrome directory will make HackerTray read the Chrome History file to mark links as read. Links are checked once every 5 minutes, which is when the History file is copied (to override the lock in case Chrome is open), searched using sqlite and deleted. This feature is still experimental.

###Google Chrome Profile Path

Where your Profile is stored depends on which version of chrome you are using:

- `google-chrome-stable`: `~/.config/google-chrome/Default/`
- `google-chrome-unstable`: `~/.config/google-chrome-unstable/Default/`
- `chromium`: `~/.config/chromium/Default/`

Replace `Default` with `Profile 1`, `Profile 2` or so on if you use multiple profiles on Chrome. Note that the `--chrome` option accepts a `PROFILE_PATH`, not the History file itself. Also note that sometimes `~` might not be set, so you might need to use the complete path (such as `/home/nemo/.config/google-chrome/Default/`).

##Features
1. Minimalist Approach to HN
2. Opens links in your default browser
3. Remembers which links you opened
4. Shows Points/Comment count in a simple format
5. Reads your Google Chrome History file to determine which links you've already read (even if you may not have opened them via HackerTray)

###Troubleshooting

If the app indicator fails to show in Ubuntu versions, consider installing 
python-appindicator with

`sudo apt-get install python-appindicator`

###Development

To develop on hackertray, or to test out experimental versions, do the following:

- Clone the project
- Run `(sudo) python setup.py develop` in the hackertray root directory
- Run `hackertray` with the required command line options from anywhere.

##Analytics
TO help improve the project and learn how its being used, I've added Analytics in hackertray. The `--dnt` switch disables all analytics so that you can opt-out if desired. All data is collected anonymously, with no machine id or user-identifying information being sent back. To learn more, and see which events are being tracked, see the [Analytics](wiki/Analytics) wiki page.

##Credits

- Mark Rickert for [Hacker Bar](http://hackerbarapp.com/).
- [Giridaran Manivannan](https://github.com/ace03uec) for troubleshooting instructions.

##Author Information
- Abhay Rana (<me@captnemo.in>)

## Donating
Support this project and [others by captn3m0][gittip] via [gittip][].

[![Support via Gittip][gittip-badge]][gittip]

[gittip-badge]: https://rawgithub.com/twolfson/gittip-badge/master/dist/gittip.png
[gittip]: https://www.gittip.com/captn3m0/

##Licence
Licenced under the [MIT Licence](http://nemo.mit-license.org/).
