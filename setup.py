import sys

from setuptools import setup
from setuptools import find_packages

requirements = ['requests']

setup(name='hackertray',
      version='4.0.2',
      description='Hacker News app that sits in your System Tray',
      long_description='HackerTray is a simple Hacker News Linux application that lets you view top HN stories in your System Tray. It supports appindicator and falls back to Gtk StatusIcon otherwise.',
      keywords='hacker news hn tray system tray icon hackertray',
      url='https://captnemo.in/hackertray',
      author='Abhay Rana (Nemo)',
      author_email='me@captnemo.in',
      license='MIT',
      packages=find_packages(),
      package_data={
          'hackertray.data': ['hacker-tray.png']
      },
      install_requires=[
          'requests>=2.23.0'
      ],
      entry_points={
          'console_scripts': ['hackertray = hackertray:main'],
      },
      zip_safe=False)
