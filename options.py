import sys, string, os, shutil

class Options:
    def __init__(self):
        """ init!"""
        self.Read_apprc()

    def Read_apprc(self):
        """ read and parse abenirc"""

        file = os.path.expanduser('~/.abeni/abenirc')
        if not os.path.exists(file):
            shutil.copy("/usr/share/abeni/abenirc", file)
        f = open(file)
        line = f.readline()
        while line:

            if string.find(line, 'browser') != -1:
                self.browser = string.strip(string.split(line, '=')[1])

            if string.find(line, 'xterm') != -1:
                self.xterm = string.strip(string.split(line, '=')[1])

            if string.find(line, 'diff') != -1:
                self.diff = string.strip(string.split(line, '=')[1])

            if string.find(line, 'editor') != -1:
                self.editor = string.strip(string.split(line, '=')[1])

            line = f.readline()
        f.close()


    def Prefs(self):
        """ Return dictionary of variables and values"""
        pref = {}
        pref['browser'] = self.browser
        pref['xterm'] = self.xterm
        pref['diff'] = self.diff
        pref['editor'] = self.editor

        return pref
