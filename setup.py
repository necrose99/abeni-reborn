#!/usr/bin/env python

from distutils.core import setup
from glob import glob

setup(name="abeni",
      version="0.0.9",
      description="Gentoo Linux ebuild GUI editor",
      author="Rob Cakebread",
      author_email="robc@myrealbox.com",
      url="http://abeni.sf.net/",
      packages=['abeni'],
      package_dir={'abeni':''},
      scripts=['bin/abeni', 'bin/repoman-safe.py'],
      data_files=[('share/pixmaps/abeni', glob("Images/*.png"))]
      )

