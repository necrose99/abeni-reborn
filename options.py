import sys, string, os, shutil

class Options:
    def __init__(self):

        """Set all var names"""
        self.pref = {}
        self.pref['browser'] = ''
        self.pref['xterm'] = ''
        self.pref['diff'] = ''
        self.pref['editor'] = ''
        self.pref['autoTabs'] = ''
        self.pref['fileBrowser'] = ''
        self.pref['use'] = ''
        self.pref['features'] = ''
        self.pref['log'] = ''
        self.pref['email'] = ''
        self.pref['statuslist'] = 'FIXED,WONTFIX,LATER,OBSOLETE,TESTING,REMIND,SUBMITTED'
        self.pref['userName'] = ''
        self.pref['cvsOptions'] = ''
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
                self.pref[var] = val
            l = f.readline()
        f.close()

    def Prefs(self):
        """Return dictionary of variables and values"""
        return self.pref
