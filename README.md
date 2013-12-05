HackerTray
==========

[![HackerTray on crate.io](https://pypip.in/v/hackertray/badge.png)](https://crate.io/packages/hackertray/)
[![HackerTray on PyPi](https://pypip.in/d/hackertray/badge.png)](https://pypi.python.org/pypi/hackertray/)
[![Build Status](https://travis-ci.org/captn3m0/hackertray.png?branch=master)](https://travis-ci.org/captn3m0/hackertray)

HackerTray is a simple [Hacker News](https://news.ycombinator.com/) Linux application
that lets you view top HN stories in your System Tray. It relies on appindicator, so
it is not guaranteed to work on all systems. It also provides a Gtk StatusIcon fallback
in case AppIndicator is not available.

The inspiration for this came from [Hacker Bar](http://hackerbarapp.com), which is 
Mac-only. I tried to port it to `node-webkit`, but had to do it in Python instead
because nw doesn't support AppIndicators yet.

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
The latest stable version is always the one [available on pip](https://pypi.python.org/pypi/hackertray/).
You can check which version you have installed with `pip freeze | grep hackertray`.

To upgrade, run `pip install -U hackertray`. In some cases (Ubuntu), you might
need to clear the pip cache before upgrading:

`sudo rm -rf /tmp/pip-build-root/hackertray`

##Features
1. Minimalist Approach to HN
2. Opens links in your default browser
3. Remembers which links you opened
4. Shows Points/Comment count in a simple format

##To-Do
- Auto Start
- Try to convert right click to comments link

##Author Information
- Abhay Rana (<me@captnemo.in>)

## Donating
Support this project and [others by captn3m0][gittip] via [gittip][].

[![Support via Gittip][gittip-badge]][gittip]

[gittip-badge]: https://rawgithub.com/twolfson/gittip-badge/master/dist/gittip.png
[gittip]: https://www.gittip.com/captn3m0/

##Licence
Licenced under the MIT Licence
