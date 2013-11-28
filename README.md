HackerTray
==========

HackerTray is a simple [Hacker News](https://news.ycombinator.com/) Linux application
that lets you view top HN stories in your System Tray. It relies on appindicator, so
it is not guaranteed to work on all systems. It also provides a StatusIcon fallback 
but it has not been tested.

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
sudo setup.py install
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


##Features
1. Minimalist Approach to HN
2. Opens links in your default browser
3. Remembers which links you opened
4. Shows Points/Comment count in a simple format

##To-Do
- Auto Start
- Try to convert right click to comments link

##Author Information
- Abhay Rana <me@captnemo.in>

##Licence
Licenced under the MIT Licence