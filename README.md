# HackerTray

[![PyPI - Version](https://img.shields.io/pypi/v/hackertray)](https://pypi.python.org/pypi/hackertray/)
[![Coverage Status](https://coveralls.io/repos/github/captn3m0/hackertray/badge.svg?branch=master)](https://coveralls.io/github/captn3m0/hackertray?branch=master)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/captn3m0/hackertray/test.yml)

HackerTray is a simple [Hacker News](https://news.ycombinator.com/) application
that lets you view top HN stories in your System Tray. On Linux it uses appindicator where available
(with a Gtk StatusIcon fallback). On macOS it uses a native status bar menu via pyobjc.

The inspiration for this came from [Hacker Bar](https://web.archive.org/web/20131126173924/http://hackerbarapp.com/) (now dead), which was Mac-only.

Over the years, this has been tested across multiple system tray implementations, including:

- Waybar on sway
- i3bar with i3
- ElementaryOS
- KDE Plasma 6.6
- GNOME 50

The new flatpak installation is in need of more testing.

## Screenshot

![HackerTray Screenshot in elementaryOS](http://i.imgur.com/63l3qXV.png)

## Installation

HackerTray is distributed as a python package. Do the following to install:

```sh
pipx install hackertray --system-site-packages
```

There is a Flatpak build and submission in progress.

### Upgrade

The latest stable version is 5.0.0.

You can check which version you have installed with `hackertray --version`.

HackerTray will automatically check the latest version on startup, and inform you if there is an update available on the command line.

## Options

HackerTray accepts its various options via the command line. Run `hackertray -h` to see all options. Currently the following switches are supported:

1.  `-c`: Enables comments support. Clicking on links will also open the comments page on HN. Can be switched off via the UI, but the setting is not remembered.
2.  `--reverse` (or `-r`): Switches the order for the elements in the menu, so Quit is at top. Use this if your system bar is at the bottom of the screen.
3.  `--verbose`: Enable debug logging.

Browser history is automatically discovered from all installed browsers (Chrome, Firefox, Safari, Brave, Edge, Arc, and many more). All profiles are searched.

Options can also be set in `~/.config/hackertray/hackertray.ini` (or `~/.config/hackertray.ini`):

## Features

1.  Minimalist Approach to HN
2.  Opens links in your default browser
3.  Shows Points/Comment count in a simple format
4.  Reads your browser history to mark which links you've already visited

### Troubleshooting

If the app indicator fails to show in Ubuntu versions, consider installing
python-appindicator with

`sudo apt-get install python-appindicator`

Note that appindicator is no longer supported in non-Ubuntu distros, because it only works on Python2.

### Development

To develop on hackertray, or to test out experimental versions, do the following:

-   Clone the project
-   Run `uv venv --system-site-packages`. This is required to allow access to the global pygobject install.
-   Run `uv run hackertray` with the required command line options

## Analytics

On every launch, a request is made to `https://pypi.python.org/pypi/hackertray/json` to check the latest version.

**No more tracking**. All data every collected for this project has been deleted. You can see [the wiki](https://github.com/captn3m0/hackertray/wiki/Analytics) for what all was collected earlier (Version `< 4.0.0`).

## Credits

-   Mark Rickert for [Hacker Bar](https://github.com/MohawkApps/Hacker-Bar) (No longer active, MIT License). The macOS port references Hacker Bar's original design.
-   [browser-history](https://github.com/browser-history/browser-history) (Apache 2.0) — browser history discovery patterns were informed by this project.
-   [Giridaran Manivannan](https://github.com/ace03uec) for troubleshooting instructions.
-   [@cheeaun](https://github.com/cheeaun) for the [Unofficial Hacker News API](https://github.com/cheeaun/node-hnapi/)

## Licence

Licenced under the [MIT Licence](https://nemo.mit-license.org/). See the LICENSE file for complete license text.
