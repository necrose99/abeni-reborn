"""options.py

This module keeps track of Abeni's preferences
and sets some sane values on first run.

"""

import sys
import os
import string
import shutil

class Options:

    """Set and store system wide preferences"""

    def __init__(self):
        """Set vars to sane values"""
        self.pref = {}
        self.pref['stripHeader'] = 1
        self.pref['clearLog'] = 1
        self.pref['checkSyntax'] = 1
        self.pref['logfile'] = 0
        self.pref['logFilename'] = os.path.expanduser("~/.abeni/log.txt")
        self.pref['font'] = "Courier,12"
        self.pref['highlighting'] = 1
        self.pref['show_whitespace'] = 0
        self.pref['tabsize'] = 4
        self.pref['gentooHighlight'] = 1
        self.pref['externalControl'] = 0
        self.pref['browser'] = '/usr/bin/firefox'
        self.pref['xterm'] = '/usr/X11R6/bin/xterm'
        self.pref['diff'] = '/usr/bin/gtkdiff'
        self.pref['editor'] = ''
        self.pref['use'] = ''
        self.pref['features'] = 'noauto'
        self.pref['cvsRoot'] = ''
        self.Read_apprc()

    def Read_apprc(self):
        """Read and parse abenirc"""
        file = os.path.expanduser('~/.abeni/abenirc')
        f = open(file)
        l = f.readline()
        while l:
            if string.find(l, '=') != -1:
                var = string.split(l, '=')[0].strip()
                val = string.split(l, '=')[1].strip()
                if val == '1' or val == 'True':
                    val = 1
                if val == '0' or val == 'False':
                    val = 0
                self.pref[var] = val
            l = f.readline()
        f.close()

    def Prefs(self):
        """Return dictionary of variables and values"""
        return self.pref
