#!/usr/bin/python

from distutils.core import setup, Extension
from glob import glob

import __version__

setup(name="abeni",
      version=__version__.version,
      description="Gentoo Linux ebuild GUI editor",
      author="Rob Cakebread",
      author_email="pythonhead@gentoo.org",
      url="http://abeni.sourceforge.net/",
      packages=['abeni', 'abeni.icons'],
      package_dir={'abeni':''},
      scripts=['bin/abeni', 'bin/abeni_ctrl'],
      data_files=[('share/pixmaps/abeni', glob("Images/*.png"))],
      py_modules = ['pyipc'],
      ext_modules=[Extension("ipcmod", ["PyIPC/ipcmod.c", 
                                        "PyIPC/ftokmod.c",
                                        "PyIPC/msgmod.c",
                                        "PyIPC/rawmem.c",
                                        "PyIPC/semmod.c",
                                        "PyIPC/shmmod.c"
                                       ]
                             )
                  ]
)

