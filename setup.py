#!/usr/bin/env python

from distutils.core import setup
from glob import glob

setup(name="abeni",
      version="0.0.1",
      description="Gentoo Linux ebuild GUI editor",
      author="Rob Cakebread",
      author_email="robc@myrealbox.com",
      url="http://abeni.sf.net/",
      packages=['abeni'],
      package_dir={'abeni':''},
      scripts=['bin/abeni'],
      data_files=[('share/bitmaps/abeni',glob("Images/*.bmp")),
                  ('share/bitmaps/abeni',glob("Images/*.png")),
                  ('share/abeni', ["abenirc"])]
      )
