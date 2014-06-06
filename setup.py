import sys

from setuptools import setup
from setuptools import find_packages


requirements = ['requests']
if sys.version_info < (2, 7):
    requirements.append('argparse')

setup(name='hackertray',
      version='2.0.1',
      description='Hacker News app that sits in your System Tray',
      long_description='HackerTray is a simple Hacker News Linux application that lets you view top HN stories in your System Tray. It relies on appindicator, so it is not guaranteed to work on all systems. It also provides a Gtk StatusIcon fallback in case AppIndicator is not available.',
      keywords='hacker news hn tray system tray icon hackertray',
      url='http://captnemo.in/hackertray',
      author='Abhay Rana',
      author_email='me@captnemo.in',
      license='MIT',
      packages=find_packages(),
      package_data={
          'hackertray.data': ['hacker-tray.png']
      },
      install_requires=[
          'requests>=2.0',
      ],
      entry_points={
          'console_scripts': ['hackertray = hackertray:main'],
      },
      zip_safe=False)
