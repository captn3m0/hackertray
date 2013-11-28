HackerTray
==========

HackerTray is a simple [Hacker News](https://news.ycombinator.com/) Linux application
that lets you view top HN stories in your System Tray. It relies on appindicator, so
it is not guaranteed to work on all systems. It also provides a StatusIcon fallback 
but it has not been tested.

The inspiration for this came from [Hacker Bar](http://hackerbarapp.com), which is 
Mac-only. I tried to port it to `node-webkit`, but had to do it in Python instead
because nw doesn't support AppIndicators yet.

##Features
1. Minimalist Approach to HN
2. Opens links in your default browser
3. Remembers which links you opened
4. Shows Points/Comment count in a simple format

##To-Do
- Auto Start
- Convert to a Python Module
- Try to convert right click to comments link

##Author Information
- Abhay Rana <me@captnemo.in>

##Licence
Licenced under the MIT Licence