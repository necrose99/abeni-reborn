#!/usr/bin/env python

from distutils.core import setup
from glob import glob

setup(name="abeni",
      version="0.0.5",
      description="Gentoo Linux ebuild GUI editor",
      author="Rob Cakebread",
      author_email="robc@myrealbox.com",
      url="http://abeni.sf.net/",
      packages=['abeni'],
      package_dir={'abeni':''},
      scripts=['bin/abeni', 'bin/repoman-safe.py'],
      data_files=[('share/pixmaps/abeni', glob("Images/*.png"))]
      )

"""
I added nulloutput.py to /usr/lib/python2.2/site-packages for
repoman-safe.py. Need to install that here somehow.
Need to credit D. Robbins for ouput.py too.
"""