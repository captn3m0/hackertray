from setuptools import setup

setup(name='hackertray',
      version='1.4',
      description='Hacker News app that sits in your System Tray',
      long_description='HackerTray is a simple Hacker News Linux application that lets you view top HN stories in your System Tray. It relies on appindicator, so it is not guaranteed to work on all systems. It also provides a Gtk StatusIcon fallback in case AppIndicator is not available.',
      keywords='hacker news hn tray system tray icon hackertray',
      url='http://captnemo.in/hackertray',
      author='Abhay Rana',
      author_email='me@captnemo.in',
      license='MIT',
      packages=['hackertray'],
      install_requires=[
          'requests',
      ],
      scripts=['bin/hackertray'],
      zip_safe=False)