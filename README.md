HackerTray
==========

HackerTray is a simple [Hacker News](https://news.ycombinator.com/) Linux application
that lets you view top HN stories in your System Tray. It relies on appindicator, so
it is not guaranteed to work on all systems.

The inspiration for this came from [Hacker Bar](http://hackerbarapp.com), which is 
Mac-only. I tried to port it to `node-webkit`, but had to do it in Python instead
because nw doesn't support AppIndicators yet.

##Features
1. Minimalist Approach to HN
2. Opens links in your default browser
3. Remembers which links you opened
4. Shows Points/Comment count in a simple format
5. 

##To-Do
- Reload data every 5 minutes
- Implement a way to remember which stories have been read
- Ideally app-memory should be persistent (save on disk)
- Auto Start
- Convert to a Python Module
- Add a menu separator between news and preferences.

##Author Information
- Abhay Rana <me@captnemo.in>

##Licence
Licenced under the MIT Licence