#!/usr/bin/env python

from distutils.core import setup
from glob import glob

setup(name="abeni",
      version="0.0.10",
      description="Gentoo Linux ebuild GUI editor",
      author="Rob Cakebread",
      author_email="pythonhead@gentoo.org",
      url="http://abeni.sourceforge.net/",
      packages=['abeni'],
      package_dir={'abeni':''},
      scripts=['bin/abeni'],
      data_files=[('share/pixmaps/abeni', glob("Images/*.png"))]
      )

