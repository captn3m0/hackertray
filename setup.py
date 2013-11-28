from setuptools import setup

setup(name='hackertray',
      version='1.1',
      description='Hacker News app that sits in your System Tray',
      url='http://github.com/captn3m0/hackertray',
      author='Abhay Rana',
      author_email='me@captnemo.in',
      license='MIT',
      packages=['hackertray'],
      install_requires=[
          'requests',
      ],
      scripts=['bin/hackertray'],
      zip_safe=False)