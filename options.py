"""options.py

This module keeps track of Abeni's preferences
and sets some sane values on first run.

"""

import os
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
        self.pref['externalControl'] = 0
        self.pref['browser'] = '/usr/bin/firefox'
        self.pref['xterm'] = '/usr/bin/xterm'
        self.pref['diff'] = '/usr/bin/gtkdiff'
        self.pref['tabPlacement'] = 0
        self.pref['logPlacement'] = 0
        self.pref['editor'] = ''
        self.pref['use'] = ''
        self.pref['features'] = 'noauto'
        self.pref['cvsRoot'] = ''
        self.pref['db'] = 0
        self.pref['extOutput'] = 1
        self.rc_create()
        self.Read_apprc()

    def rc_create(self):
        """Copy skeleton rcfile into abeni dir if needed"""
        abeniDir = os.path.expanduser('~/.abeni')
        if not os.path.exists(abeniDir):
            print "Creating ~/.abeni"
            os.mkdir(abeniDir)
        if not os.path.exists(os.path.expanduser("~/.abeni/emerge_log")):
            try:
                os.system("touch %s/emerge_log" % os.path.expanduser("~/.abeni/"))
            except:
                print "!!! This file must be owned by you: %s" % os.path.expanduser("~/.abeni/emerge_log")
                sys.exit(1)
        rcfile = '%s/abenirc' % abeniDir
        if not os.path.exists(rcfile):
            print "Creating ~/.abeni/abenirc"
            shutil.copy("/usr/share/abeni/abenirc", rcfile)

    def Read_apprc(self):
        """Read and parse abenirc"""
        fname = os.path.expanduser('~/.abeni/abenirc')
        f = open(fname)
        l = f.readline()
        while l:
            if l.find('=') != -1:
                var = l.split("=")[0].strip()
                val = l.split("=")[1].strip()
                if val == '1' or val == 'True':
                    val = 1
                if val == '0' or val == 'False':
                    val = 0
                if val == '2':
                    val = 2
                if val == '3':
                    val = 3
                if val == '4':
                    val = 4
                if val == '5':
                    val = 5
                self.pref[var] = val
            l = f.readline()
        f.close()

    def Prefs(self):
        """Return dictionary of variables and values"""
        return self.pref
