#!/usr/bin/python

"""Abeni - Gentoo Linux Ebuild Integrated Development Environment
"""

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

__author__ = 'Rob Cakebread'
__email__ = 'pythonhead@gentoo.org'
__changelog_ = 'http://abeni.sourceforge.net/ChangeLog'


import os
import string
import sys
import time
import re
import shutil
#import tarfile (when Abeni depends on Python 2.3)

from portage import config, settings
from wxPython.wx import *

import gui
import __version__


try:
    env = config(clone=settings).environ()
except:
    print "ERROR: Can't read portage configuration from /etc/make.conf"
    sys.exit(1)

distdir = env['DISTDIR']
portdir = env['PORTDIR']

#Exit if they don't have PORTDIR_OVERLAY defined in /etc/make.conf
# or if defined but directory doesn't exist.
#TODO: Pop up a dialog instead (MyMessage)
try:
    #Users may specify multiple overlay directories, we use the first one:
    portdir_overlay = env['PORTDIR_OVERLAY'].split(" ")[0]
    if portdir_overlay[-1] == "/":
        portdir_overlay = portdir_overlay[:-1]
except:
    print "ERROR: You must define PORTDIR_OVERLAY in your /etc/make.conf"
    print "You can simply uncomment this line:"
    print "#PORTDIR_OVERLAY='/usr/local/portage'"
    print "Then: mkdir /usr/local/portage"
    sys.exit(1)
if not portdir_overlay:
    print "ERROR: Create the directory PORTDIR_OVERLAY in /etc/make.conf"
    sys.exit(1)

portage_tmpdir = env['PORTAGE_TMPDIR']
#Lets choose the first arch they have, in case of multiples.
#TODO: Mention in documentation
arch = '~%s' % env['ACCEPT_KEYWORDS'].split(' ')[0].replace('~', '')

class MyApp(wxPySimpleApp):

    """ Main wxPython app class """

    def OnInit(self):
        """Set up the main frame"""
        # Enable gif, jpg, bmp, png handling for wxHtml and icons
        wxInitAllImageHandlers()
        self.frame=gui.MyFrame(None,-1, 'Abeni - The ebuild Builder ' + \
                               __version__.version)
        self.frame.Show(true)
        self.SetTopWindow(self.frame)
        return true


app=MyApp()
app.MainLoop()
