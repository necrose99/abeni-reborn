#!/usr/bin/env python

"""Abeni - Gentoo Linux Ebuild Editor/Syntax Checker
Released under the terms of the GNU Public License v2"""

__author__ = 'Rob Cakebread'
__email__ = 'robc@myrealbox.com'
__version__ = '0.0.7'
__changelog_ = 'http://abeni.sf.net/ChangeLog'

print "Importing portage config, wxPython, Python and Abeni modules..."

from portage import config, portdb, db
from wxPython.wx import *
from wxPython.lib.dialogs import wxScrolledMessageDialog
import os, string, sys, urlparse, time, re
#Abeni modules:
import dialogs, panels
from utils import *

#Is there a better way?
modulePath = "/usr/lib/python%s/site-packages/abeni" % sys.version[0:3]

try:
    env = config().environ()
except:
    print "ERROR: Can't read portage configuration from /etc/make.conf"
    sys.exit(1)

distdir = env['DISTDIR']
portdir = env['PORTDIR']

#Exit if they don't have PORTDIR_OVERLAY defined in /etc/make.conf
# or if defined but directory doesn't exist.
try:
    #Users may specify multiple overlay directories, we use the first one:
    portdir_overlay = env['PORTDIR_OVERLAY'].split(" ")[0]
except:
    print "ERROR: You must define PORTDIR_OVERLAY in your /etc/make.conf"
    print "You can simply uncomment this line:"
    print "#PORTDIR_OVERLAY='/usr/local/portage'"
    print "Then: mkdir /usr/local/portage"
    sys.exit(1)
if not portdir_overlay:
    print "ERROR: Please create the directory defined in /etc/make.conf as PORTDIR_OVERLAY"
    sys.exit(1)

portage_tmpdir = env['PORTAGE_TMPDIR']
arch = '~%s' % env['ACCEPT_KEYWORDS'].split(' ')[0].replace('~', '')

defaults = ["SRC_URI", "HOMEPAGE", "DEPEND", "RDEPEND", "DESCRIPTION", \
            "S", "IUSE", "SLOT", "KEYWORDS", "LICENSE"]

class MyFrame(wxFrame):

    """ Main frame that holds the menu, toolbar and notebook """

    def __init__(self, parent, id, title):
        wxFrame.__init__(self, parent, -1, title, size=wxSize(900,600))

        #Catch the close event so we can clean up nicely.
        EVT_CLOSE(self,self.OnClose)
        # Are we in the process of editing an ebuild?
        self.editing = 0
        #Load recently accessed ebuilds
        if not os.path.exists(os.path.expanduser('~/.abeni')):
            print "Creating directory " + os.path.expanduser('~/.abeni')
            os.mkdir(os.path.expanduser('~/.abeni'))
        if not os.path.exists(os.path.expanduser('~/.abeni/bugzilla')):
            os.mkdir(os.path.expanduser('~/.abeni/bugzilla'))
        bookmarks = os.path.expanduser('~/.abeni/recent.txt')
        if os.path.exists(bookmarks):
            self.recentList = open(bookmarks, 'r').readlines()
        else:
            self.recentList = []
        # Get options from ~/.abeni/abenirc file
        GetOptions(self)
        # Custom functions added instances
        self.funcList = []
        #Misc statements/commands instances
        self.statementList = []
        # Keep track of order variables are set
        self.varOrder = []
        # Keep track of order functions are set
        self.funcOrder = []
        # Ebuild's path and filename
        self.filename = ''
        # Previous file opened. For use with diff
        self.lastFile = ''
        # Saved state
        self.saved = 1
        # Tells if an external command is running, like emerge, ebuild etc.
        self.running = None
        # Action performed during external commands
        self.action = None
        # Ordered list of notebook tabs
        self.tabs = []
        self.tabsInstance = []

        #Stuff to keep log window updating in "real-time" as shell commands are executed
        self.process = None
        EVT_IDLE(self, self.OnIdle)
        EVT_END_PROCESS(self, -1, self.OnProcessEnded)

        # Setting for noauto toggle button
        self.StripNoAuto()
        self.noauto = 1

        #application icon 16x16
        iconFile = ('/usr/share/pixmaps/abeni/abeni_logo16.png')
        icon = wxIcon(iconFile, wxBITMAP_TYPE_PNG)
        self.SetIcon(icon)
        #AddMenu(self)

        self.MyMenu()

        AddToolbar(self)
        self.sb = self.CreateStatusBar(2, wxST_SIZEGRIP)
        self.splitter = wxSplitterWindow(self, -1, style=wxNO_3D|wxSP_3D)
        def EmptyHandler(evt): pass
        EVT_ERASE_BACKGROUND(self.splitter, EmptyHandler)
        self.nb = wxNotebook(self.splitter, -1, style=wxCLIP_CHILDREN)
        EVT_NOTEBOOK_PAGE_CHANGED(self.nb, -1, self.OnPageChanged)
        EVT_NOTEBOOK_PAGE_CHANGED(self.nb, -1, self.OnPageChanging)
        #TODO, just pass the env dict
        self.nb.portdir_overlay = portdir_overlay
        self.nb.portdir = portdir
        self.log = wxTextCtrl(self.splitter, -1,
                             style = wxTE_MULTILINE|wxTE_READONLY|wxHSCROLL|wxTE_RICH2)
        self.log.SetFont(wxFont(12, wxMODERN, wxNORMAL, wxNORMAL, faceName="Lucida Console"))
        #This would be nice, but some .gtkrc files screw it up:
        #self.log.SetBackgroundColour(wxBLACK)
        #self.log.SetDefaultStyle(wxTextAttr(wxWHITE))
        #self.log.SetDefaultStyle(wxTextAttr(wxNullColour, wxBLACK))

        wxLog_SetActiveTarget(MyLog(self.log))
        self.Show(True)
        self.splitter.SplitHorizontally(self.nb, self.log, 400)
        self.sashPosition = 400
        #Load ebuild if specified on command line, by filename or by full package name
        if len(sys.argv) == 2:
            f = sys.argv[1]
            if os.path.exists(f):
                LoadEbuild(self, f, portdir)
            else:
                print "No such file: %s" % f
                print "Checking for package: %s" % f
                #Make sure GUI is drawn before we start the slow search
                wxSafeYield()
                self.LoadByPackage(f)

    def OnMnuBugzSum(self, event):
        import ProjectManager
        frame = ProjectManager.MyFrame(None, self.write)
        frame.Show(true)

    def OnMnuGetDeps(self, event):
        l = self.panelDepend.elb1.GetStrings()
        new = []
        for p in l:
            p = p.strip()
            if p:
                #curver = self.versions('^%s$' % p)
                curver = self.versions(p)
                if curver == None:
                    self.write("Can't find: %s" % p)
                    new.append(p)
                elif curver == "":
                    #self.write("Multiple names like %s. Be more specific." % p)
                    #Also means isn't installed. TODO
                    self.write(p)
                    new.append(p)
                else:
                    self.write(">=%s" % curver)
                    new.append(">=%s" % curver)
        self.panelDepend.elb1.SetStrings(new)

    def search(self, search_key):
        matches = []
        for package in portdb.cp_all():
            package_parts=package.split("/")
            if re.search(search_key.lower(), package_parts[1].lower()):
                matches.append(package)
        return matches

    def versions(self, query):
        tup = self.smart_pkgsplit(query)
        if tup[0] and tup[1]:
            matches = [ tup[0] + "/" + tup[1] ]
        elif tup[1]:
            matches = self.search(tup[1])
        curver = ""
        for package in matches:
            curver = db["/"]["vartree"].dep_bestmatch(package)
            return curver

    def smart_pkgsplit(self, query):
        cat = ''
        pkg = ''
        ver = ''
        rev = ''

        if len(query.split('/')) == 2:
            cat = query.split('/')[0]
            query = query.split('/')[1]

        components = query.split('-')
        name_components = []
        ver_components = []

        # seperate pkg-ver-rev
        for c in components:
            if ver_components:
                ver_components.append(c)
            elif ord(c[0]) > 47 and ord(c[0]) < 58:
                ver_components.append(c)
            else:
                name_components.append(c)
        pkg = '-'.join(name_components)

        # check if there is a revision number
        if len(ver_components) > 0 and ver_components[-1][0] == 'r':
            rev = ver_components[-1]
            ver_components = ver_components[:-1]

        # check for version number
        if len(ver_components) > 0:
            ver = '-'.join(ver_components)

        return [cat, pkg, ver, rev]

    def __del__(self):
        if self.process is not None:
            self.process.Detach()
            self.process.CloseOutput()
            self.process = None

    def MyMessage(self, msg, title, type="info"):
            if type == "info":
                icon = wxICON_INFORMATION
            elif type == "error":
                icon = wxICON_ERROR

            dlg = wxMessageDialog(self, msg, title, wxOK | icon)
            dlg.ShowModal()
            dlg.Destroy()

    def OnMnuLogBottom(self, event):
        """Switch ouput log to bottom"""
        if not self.editing or self.pref['log'] == 'bottom':
            return
        if self.pref['log'] == 'window':
            self.logWin.Close()
        else:
            self.splitter.SplitHorizontally(self.nb, self.log, 400)
            self.splitter.SetMinimumPaneSize(20)
            self.log.Show(True)
            self.log.ShowPosition(self.log.GetLastPosition())
            self.pref['log'] = 'bottom'

    def LogBottom(self, log):
        self.menu_options.Check(self.mnuLogBottomID, 1)
        self.log = log
        self.log.Reparent(self.splitter)
        wxLog_SetActiveTarget(MyLog(self.log))
        self.splitter.SplitHorizontally(self.nb, self.log, 400)
        self.splitter.SetMinimumPaneSize(20)
        self.log.Show(True)
        self.log.ShowPosition(self.log.GetLastPosition())
        self.pref['log'] = 'bottom'

    def LogWindow(self):
        #Show log in separate window
        if self.splitter.IsSplit():
            self.splitter.Unsplit()
            self.logWin=panels.LogWindow(self)
            self.logWin.Show(True)
            self.log.Show(True)
            self.pref['log'] = 'window'
            self.menu_options.Check(self.mnuLogWindowID, 1)

    def OnMnuLogWindow(self, event):
        """Switch ouput log to separate window"""
        if not self.editing or self.pref['log'] == 'window':
            return
        self.LogWindow()
        #self.log.ShowPosition(self.log.GetLastPosition())

    def OnNoAuto(self, event):
        """Toggle switch for FEATURES='noauto'"""
        self.StripNoAuto()
        if self.noauto == 1:
            self.noauto = 0
            self.pref['features'] = "noauto %s" % self.pref['features'].strip()
        else:
            self.noauto = 1
            self.pref['features'] = "-noauto %s" % self.pref['features'].strip()

    def StripNoAuto(self):
        """Strip noauto feature"""
        #We completely ignore what's in make.conf and Abeni's preference file because this switch is so damned handy
        if string.find(self.pref['features'], "-noauto") != -1:
            self.pref['features'] = string.replace(self.pref['features'], "-noauto", "")
        if string.find(self.pref['features'], "noauto") != -1:
            self.pref['features'] = string.replace(self.pref['features'], "noauto", "")

    def OnMnuClearLog(self, event):
        """Blank out the log windows"""
        self.log.SetValue('')

    def WriteText(self, text):
        """Send text to log window after colorizing"""
        if text[-1:] == '\n':
            text = text[:-1]
        color = ''
        reset = "\x1b[0m"
        if string.find(text, reset) != -1:
            codes={}
            codes["bold"]="\x1b[01m"
            codes["teal"]="\x1b[36;06m"
            codes["turquoise"]="\x1b[36;01m"
            codes["fuscia"]="\x1b[35;01m"
            codes["purple"]="\x1b[35;06m"
            codes["blue"]="\x1b[34;01m"
            codes["darkblue"]="\x1b[34;06m"
            codes["green"]="\x1b[32;01m"
            codes["darkgreen"]="\x1b[32;06m"
            codes["yellow"]="\x1b[33;01m"
            codes["brown"]="\x1b[33;06m"
            codes["red"]="\x1b[31;01m"
            codes["darkred"]="\x1b[31;06m"
            text = string.replace(text, reset, '')
            for c in codes:
                if string.find(text, codes[c]) != -1:
                    if c == "darkgreen":
                        color = "FOREST GREEN"
                    elif c == "yellow":
                        color = "BROWN"
                    elif c == "brown":
                        color = "BROWN"
                    elif c == "darkred":
                        color = "RED"
                    elif c == "teal":
                        color = "FOREST GREEN"
                    elif c == "turquoise":
                        color = "TURQUOISE"
                    elif c == "fuscia":
                        color = "PURPLE"
                    elif c == "green":
                        color = "DARK GREEN"
                    elif c == "red":
                        color = "RED"
                    else:
                        color = "BLUE"
                    text = string.replace(text, codes[c], '')
                    break
        if color:
            self.logColor(color)
            wxLogMessage(text)
            self.logColor("BLACK")
        else:
            if text[0:3] == ">>>" or text[0:3] == "<<<":
                self.logColor("BLUE")
                wxLogMessage(text)
                self.logColor("BLACK")
            elif text[0:3] == "!!!":
                self.logColor("RED")
                wxLogMessage(text)
                self.logColor("BLACK")
            else:
                wxLogMessage(text)

    def logColor(self, color):
        """Set color of text sent to log window"""
        self.log.SetDefaultStyle(wxTextAttr(wxNamedColour(color)))

    def write(self, txt):
        """Send text to log window"""
        self.WriteText(txt)

    def GetP(self):
        ebuild = self.panelMain.EbuildFile.GetValue()
        p = string.replace(ebuild, '.ebuild', '')
        return p

    def OnToolbarXterm(self, event):
        """Launch xterm in PORTAGE_TMPDIR/portage/P/"""
        #TODO: Damn it. I wish we could cd to ${S}
        if not self.editing:
            return
        if not self.CheckUnpacked():
            msg = 'You need to unpack the package first.'
            title = 'Error'
            self.MyMessage(msg, title, "error")
        else:
            c = os.getcwd()
            p = self.GetP()
            os.chdir('%s/portage/%s' % (portage_tmpdir, p))
            os.system('sudo %s &' % self.pref['xterm'])
            os.chdir(c)

    def OnMnuNewVariable(self, event):
        """Dialog for adding new variable"""
        if not self.editing:
            return
        dlg = wxTextEntryDialog(self, 'New Variable Name:',
                            'Enter Variable Name', 'test')
        dlg.SetValue("")
        if dlg.ShowModal() == wxID_OK:
            newVariable = dlg.GetValue()
            self.varOrder.append(newVariable)
            self.AddNewVar(newVariable, "")
        self.saved = 0
        dlg.Destroy()

    def AddNewVar(self, var, val):
        """Add new variable on Main panel"""
        if val == '':
            val = '""'
        self.panelMain.AddVar(var, val)

    def OnMnuDelVariable(self, event):
        """Delete custom variable"""
        if not self.editing:
            return
        self.saved = 0
        DelVariable(self)

    def AddCommand(self, command):
        t = self.panelMain.stext.GetValue()
        t += "%s\n" % command
        self.panelMain.stext.SetValue(t)

    def OnMnuEdit(self, event):
        """Launch external editor then reload ebuild after editor exits"""
        if self.editing:
            self.SaveEbuild()
            self.ClearNotebook()
            #Don't run sudo, we want user owner/perms on ebuild files in PORTDIR_OVERLAY
            wxSafeYield()
            os.system('%s %s' % (self.pref['editor'], self.filename))
            LoadEbuild(self, self.filename, portdir)

    def OnMnuDiff(self, event):
        """Run diff program on original vs. saved ebuild"""
        #TODO Add error dialog if last opened wasn't same package, or is empty
        if not self.editing:
            return
        if self.lastFile:
            os.system("%s %s %s &" % (self.pref['diff'], self.lastFile, self.filename))

    def OnMnuDiffCreate(self, event):
        """Create diff file of original vs. saved ebuild"""
        #TODO: Add error dialog if last opened wasn't same package, or is empty
        # Add dialog telling them file is saved in ~/.abeni/diffFile
        if not self.editing:
            return

        #No file to compare with
        if not self.lastFile:
            return
        diffFile = string.replace(self.ebuild_file, '.ebuild', '.diff')
        cmd = 'diff -u %s %s > ~/.abeni/%s' % (self.lastFile, self.filename, diffFile)
        self.ExecuteInLog(cmd)

    def OnMnuRepoman(self, event):
        """Run 'repoman-local-5.py' on this ebuild"""
        if not self.editing:
            return
        cmd = 'cd %s;/usr/bin/repoman-safe.py' % self.ebuildDir
        self.ExecuteInLog(cmd)

    def OnMnuEmerge(self, event):
        """Run 'emerge <options> <this ebuild>' """
        if not self.editing:
            return
        if self.SaveEbuild():
            win = dialogs.EmergeDialog(self, -1, "Enter emerge options", \
                                size=wxSize(350, 350), \
                                style = wxDEFAULT_DIALOG_STYLE \
                                )
            win.CenterOnScreen()
            val = win.ShowModal()
            emergeCmd = win.emerge.GetValue()
            use = win.use.GetValue()
            features = win.features.GetValue()
            if emergeCmd[:6] != 'emerge':
                self.write("Error, can't run: %s " % emergeCmd)
                return
            if val == wxID_OK:
                cmd = 'USE="%s" FEATURES="%s" sudo %s' % (use, features, emergeCmd)
                self.write(cmd)
                self.ExecuteInLog(cmd)

    def OnMnuEbuild(self, event):
        """Run 'ebuild <file> <cmd>' """
        if not self.editing:
            return
        c = ['setup', 'depend', 'merge', 'qmerge', 'unpack',
             'compile', 'rpm', 'package', 'prerm', 'postrm',
             'preinst', 'postinst', 'config', 'touch', 'clean',
             'fetch', 'digest', 'install', 'unmerge']
        c.sort()
        dlg = wxSingleChoiceDialog(self, 'Command:', 'ebuild command',
                                   c, wxOK|wxCANCEL)
        if dlg.ShowModal() == wxID_OK:
            opt = dlg.GetStringSelection()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        if self.SaveEbuild():
            cmd = 'USE="%s" FEATURES="%s" sudo /usr/sbin/ebuild %s %s' % (self.pref['use'], self.pref['features'], self.filename, opt)
            self.write('Executing:\n%s' % cmd)
            self.ExecuteInLog(cmd)

    def OnIdle(self, event):
        if self.process is not None:
            stream = self.process.GetInputStream()
            if stream.CanRead():
                t = stream.readline()
                self.write(t)

    def OnProcessEnded(self, evt):
        #self.log.write('OnProcessEnded, pid:%s,  exitCode: %s\n' %
        #               (evt.GetPid(), evt.GetExitCode()))
        stream = self.process.GetInputStream()
        if stream.CanRead():
            text = stream.read()
            text = string.split(text, '\n')
            for t in text:
                self.write(t)
        self.process.Destroy()
        self.process = None
        self.tb.EnableTool(self.toolStopID, False)
        self.running = None
        self.log.ShowPosition(self.log.GetLastPosition())
        action = self.action
        self.action = None
        self.PostAction(action)

    def PostAction(self, action):
        if action == 'unpack':
            ebuild = self.panelMain.EbuildFile.GetValue()
            p = string.replace(ebuild, '.ebuild', '')
            d = '%s/portage/%s/work' % (portage_tmpdir, p)
            self.logColor("RED")
            self.write("Unpacked these directory(s) into ${WORKDIR}:")
            self.logColor("BLACK")
            self.ExecuteInLog('sudo ls %s' % d)
            self.ViewConfigure()
            self.ViewMakefile()

    def ExecuteInLog(self, cmd):
        if self.running:
            msg = ("Please wait till this finishes:\n %s" % self.running)
            title = 'Abeni: Error - Wait till external program is finished.'
            self.MyMessage(msg, title, "error")
            return
        self.running = cmd
        self.tb.EnableTool(self.toolStopID, True)
        self.process = wxProcess(self)
        self.process.Redirect();
        pyCmd = "python -u %s/doCmd.py %s" % (modulePath, cmd)
        self.pid = wxExecute(pyCmd, wxEXEC_ASYNC, self.process)
        #self.write('"%s" pid: %s\n' % (cmd, pid))

    def KillProc(self, event):
        os.system("sudo kill %s" % self.pid)
        self.write("Killed %s" % self.pid)
        try:
            pid = open("/tmp/abeni_proc.pid", "r").read().strip()
            os.system("sudo kill %s" % pid)
            self.write("sub pid %s killed" % pid)
        except:
            pass

    def OnMnuLintool(self, event):
        """Run 'lintool' on this ebuild"""
        if not self.editing:
            return
        cmd = '/usr/bin/lintool %s' % self.filename
        self.ExecuteInLog(cmd)

    def ClearNotebook(self):
        """Delete all pages in the notebook"""
        self.nb.DeleteAllPages()
        self.funcList = []
        self.statementList = []
        self.funcOrder = []
        self.varOrder = []
        # Stupid kludge. See TODO
        x,y  = self.GetSize()
        self.SetSize(wxSize(x+1, y))

    def SetFilename(self, filename):
        """Set the ebuild full path and filename"""
        #Keep last file for viewing and creating diffs
        self.lastFile = self.filename
        self.filename = filename
        self.sb.SetStatusText(filename, 1)

    def GetFilename(self):
        """Get the full path and filename of ebuild"""
        return self.filename

    def SeparateVars(self, vars):
        """Separates variables into defaultVars and all others (vars)"""
        defaultVars = {}
        for key in defaults:
            if vars.has_key(key):
                defaultVars[key] = vars[key]
                del vars[key]
            else:
                defaultVars[key] = ""
        return defaultVars, vars

    def VerifySaved(self):
        modified = 0
        status = 0
        for fns in self.funcList:
            if fns.edNewFun.GetModify():
                modified = 1
                break
        if modified or not self.saved:
            dlg = wxMessageDialog(self, 'Save modified ebuild?\n' + self.filename,
                    'Save ebuild?', wxYES_NO | wxCANCEL | wxICON_INFORMATION)
            val = dlg.ShowModal()
            if val == wxID_YES:
                WriteEbuild(self)
                self.saved = 1
                status = 0
            if val == wxID_NO:
                status = 0
            if val == wxID_CANCEL:
                status = 1
            dlg.Destroy()
        return status

    def OnFileHistory(self, evt):
        """Load ebuild on FileHistory event"""
        # get the file based on the menu ID
        fileNum = evt.GetId() - wxID_FILE1
        path = self.filehistory.GetHistoryFile(fileNum)
        if os.path.exists(path) and not self.VerifySaved():
            self.ClearNotebook()
            LoadEbuild(self, path, portdir)
            # add it back to the history so it will be moved up the list
            self.filehistory.AddFileToHistory(path)

    def OnMnuLoad(self, event):
        """Load ebuild file"""
        if not self.VerifySaved():
            wildcard = "ebuild files (*.ebuild)|*.ebuild"
            dlg = wxFileDialog(self, "Choose a file", portdir, "", \
                                wildcard, wxOPEN)
            if dlg.ShowModal() == wxID_OK:
                filename = dlg.GetPath()
                if os.path.exists(filename):
                    if self.editing:
                        self.ClearNotebook()
                    LoadEbuild(self, filename, portdir)
                    self.filehistory.AddFileToHistory(filename)
            dlg.Destroy()

    def PopulateForms(self, defaultVars):
        """Fill forms with saved data"""
        self.panelMain.Package.SetValue(defaultVars['package'])
        self.package = defaultVars['package']
        self.panelMain.EbuildFile.SetValue(defaultVars['ebuild_file'])
        self.panelMain.Category.SetValue(defaultVars['category'])
        self.panelMain.URI.SetValue(defaultVars['SRC_URI'])
        self.panelMain.Homepage.SetValue(defaultVars['HOMEPAGE'])
        self.panelMain.Desc.SetValue(defaultVars['DESCRIPTION'])
        self.panelMain.S.SetValue(defaultVars['S'])
        self.panelMain.USE.SetValue(defaultVars['IUSE'])
        self.panelMain.Slot.SetValue(defaultVars['SLOT'])
        self.panelMain.Keywords.SetValue(defaultVars['KEYWORDS'])
        self.panelMain.License.SetValue(defaultVars['LICENSE'])
        d = string.split(defaultVars['DEPEND'], '\n')
        depends = []
        for s in d:
            s = s.replace('"', '')
            depends.append(s)
        self.panelDepend.elb1.SetStrings(depends)
        r = string.split(defaultVars['RDEPEND'], '\n')
        rdepends = []
        for s in r:
            s = s.replace('"', '')
            rdepends.append(s)
        self.panelDepend.elb2.SetStrings(rdepends)

    def OnPageChanging(self, event):
        """Catch event when page in notebook is going to change"""
        #self.tab[n] = labels
        to = event.GetSelection()
        current = event.GetOldSelection()
        #Remember sash position on all pages except Main and Dependencies
        if current != 0 and current != 1:
            self.sashPosition = self.splitter.GetSashPosition()
        else:
            self.splitter.SetSashPosition(self.sashPosition)
        event.Skip()

    def OnPageChanged(self, event):
        """Catch event when page in notebook is changed"""
        #Keep the sash from moving up over Main panel:
        n = self.nb.GetSelection()
        if n == 0 or n == 1:
            if self.pref['log'] == 'bottom':
                self.splitter.SetSashPosition(400)

        #if self.tabs[n] == 'Ebuild File':
            #WriteEbuild(self)
            #self.ebuildfile.editorCtrl.SetText(open(self.filename, 'r').read())
            #pass
        event.Skip()

    def OnMnuEclassCVS(self, event):
        """Add Python distutils-related variables, inherit etc."""
        print "Adding CVS skel\n"
        if not self.editing:
            return
        self.write("Adding CVS skel\n")
        EclassCVS(self)

    def OnMnuEclassDistutils(self, event):
        """Add CVS-related variables, inherit etc."""
        if not self.editing:
            return
        EclassDistutils(self)

    def OnMnuEclassGames(self, event):
        """Add games.eclass inherit, default funcs"""
        if not self.editing:
            return
        EclassGames(self)

    def OnMnuBugzilla(self, event):
        """Dialog to add bugzilla info"""
        if not self.editing:
            return
        dlg = dialogs.BugzillaDialog(self)
        dlg.CenterOnScreen()
        v = dlg.ShowModal()
        if v == wxID_OK:
            self.write( "Saving.")
            r = dlg.SaveInfo()
        dlg.Destroy()

    def OnMnuNewFunction(self, event):
        """Dialog to add new function"""
        if not self.editing:
            return
        #from NewFuncDialog import wxDialog1
        dlg = dialogs.NewFunction(self)
        dlg.CenterOnScreen()
        v = dlg.ShowModal()
        if v == wxID_OK:
            func, val = dlg.GetFunc()
            self.AddFunc(func, val)
        self.saved = 0
        dlg.Destroy()

    def NewPage(self, panel, name):
        self.nb.AddPage(panel, name)
        self.tabs.append(name)
        #self.tabsInstance.append(panel)
        #print self.tabsInstance
        #print self.tabs

    def AddFunc(self, newFunction, val):
        """Add page in notebook for a new function"""
        #TODO don't pass sb, pref if not necessary
        n = panels.NewFunction(self.nb)
        self.funcList.append(n)
        self.NewPage(n, newFunction)
        n.edNewFun.SetText(val)
        n.edNewFun.SetSavePoint()
        self.nb.SetSelection(self.nb.GetPageCount() -1)

    def OnMnuDelFunction(self, event):
        """Remove current function page"""
        #TODO: This removes any page, change to only move functions.
        p = self.nb.GetSelection()
        check = self.nb.GetPage(p)
        n = 0
        for f in self.funcList:
            if f == check:
                self.nb.SetSelection(p-1)
                self.nb.RemovePage(p)
                del self.tabs[p]
                x,y  = self.GetSize()
                self.SetSize(wxSize(x+1, y))
                break
            n += 1
        del self.funcList[n]
        self.saved = 0

    def AddEditor(self, name, val):
        """Add page in notebook for an editor"""
        n = panels.Editor(self.nb)
        self.NewPage(n, name)
        n.editorCtrl.SetText(val)
        if name == 'Output':
            n.editorCtrl.SetReadOnly(1)
            self.ebuildfile = n
        if name == 'configure' or name == 'Makefile' or name == 'Environment':
            n.editorCtrl.SetReadOnly(1)

    def OnMnuHelpRef(self, event):
        """Display html help file"""
        os.system(self.pref['browser'] + " 'http://abeni.sf.net/docs/ebuild-quick-reference.html' &")

    def OnMnuHelp(self, event):
        """Display html help file"""
        #TODO:
        #Add: PORTDIR/profiles/use.desc
        os.system(self.pref['browser'] + " 'http://abeni.sf.net/docs/index.html' &")

    def OnMnuSave(self, event):
        """Save ebuild file to disk"""
        if not self.editing:
            return
        self.SaveEbuild()

    def SaveEbuild(self):
        msg = self.checkEntries()
        if not msg:
            defaultVars = getDefaultVars(self)
            WriteEbuild(self)
            self.saved = 1
            self.DoTitle()
            return 1
        else:
            title = 'Abeni: Error Saving'
            self.MyMessage(msg, title, "error")
            return 0

    def checkEntries(self):
        """Validate entries on forms"""
        # We're checking category and license now.
        # TODO: Do sanity checking, like package, ebuild name ($P, $EBUILD)
        category = self.panelMain.Category.GetValue()
        categoryDir = self.GetCategory()
        valid_cat = os.path.join(portdir, category)
        if categoryDir == portdir_overlay + '/':
            msg = "You must specify a category."
            return msg
        if not os.path.exists(valid_cat):
            msg = category + " isn't a valid category."
            return msg

    def OnMnuNew(self,event):
        """Creates a new ebuild from scratch"""
        #TODO:
        # Show dialog if URI isn't properly formed or can't determine package, filename, ebuild name
        if not self.VerifySaved():
            win = dialogs.GetURIDialog(self, -1, "Enter Package URI", \
                                size=wxSize(350, 200), \
                                style = wxDEFAULT_DIALOG_STYLE \
                                )
            win.CenterOnScreen()
            val = win.ShowModal()
            self.URI = win.URI.GetValue()
            if self.URI == 'http://' or self.URI == '':
                return
            if val == wxID_OK and self.URI:
                self.ClearNotebook()
                self.AddPages()
                self.AddEditor("Output", "")
                if self.pref['log'] == 'window':
                    self.LogWindow()
                self.panelMain.PopulateDefault()
                self.write(self.URI)
                if self.URI == "CVS" or self.URI == "cvs":
                    #self.panelMain.SetURI("package-cvs-0.0.1")
                    self.panelMain.SetName("package-cvs-0.0.1")
                else:
                    if self.URI.find('sourceforge') != -1:
                        #http://umn.dl.sourceforge.net/sourceforge/tikiwiki/tiki161.zip
                        #mirror://sourceforge/tikiwiki/tiki161.ip
                        #a = urlparse.urlparse("http://umn.dl.sourceforge.net/sourceforge/tikiwiki/tiki161.zip")
                        #('http', 'umn.dl.sourceforge.net', '/sourceforge/tikiwiki/tiki161.zip', '', '', '')
                        a = urlparse.urlparse(self.URI)
                        self.URI='mirror:/%s' % a[2]
                    self.panelMain.SetURI(self.URI)
                    self.panelMain.SetName(self.URI)
                self.panelMain.SetPackage()
                if self.URI.find('sourceforge') != -1:
                    self.panelMain.Homepage.SetValue('"http://sourceforge.net/projects/%s"' % self.panelMain.GetPackage().lower())
                self.panelChangelog.Populate("%s/skel.ChangeLog" % portdir, portdir)
                self.editing = 1
                self.saved = 0
                if self.URI == "CVS" or self.URI == "cvs":
                    self.OnMnuEclassCVS(-1)
                self.DoTitle()
                if self.pref['log'] == 'window':
                    self.nb.SetSelection(1)

    def DoTitle(self):
        if not self.saved:
            self.SetTitle(self.panelMain.GetEbuildName() + " * Abeni " + __version__)
        else:
            self.SetTitle(self.panelMain.GetEbuildName() + " - Abeni " + __version__)

    def AddPages(self):
        """Add pages to blank notebook"""
        self.panelMain=panels.main(self.nb, env)
        self.panelDepend=panels.depend(self.nb)
        self.panelChangelog=panels.changelog(self.nb)
        self.NewPage(self.panelMain, "Main")
        self.NewPage(self.panelDepend, "Dependencies")
        self.NewPage(self.panelChangelog, "ChangeLog")

    def OnClose(self, event):
        """Called when trying to close application"""
        #TODO: Give yes/no quit dialog.
        if self.running:
            self.write("You're executing %s" % self.running)
            return

        if not self.VerifySaved():
            bookmarks = os.path.expanduser('~/.abeni/recent.txt')
            f = open(bookmarks, 'w')
            for ebuild in self.recentList:
                if ebuild != '\n':
                    l = string.strip(ebuild)
                    f.write(l + '\n')
            f.close()
            print "Exited safely."
            self.Destroy()

    def OnMnuExit(self,event):
        """Exits and closes application"""
        self.OnClose(-1)

    def OnMnuUseHelp(self, event):
        """View PORTDIR/profiles/use.desc file"""
        f = "%s/profiles/use.desc" % portdir
        msg = open(f, "r").read()
        dlg = wxScrolledMessageDialog(self, msg, "USE descriptions")
        dlg.Show(True)

    def OnMnuEclassHelp(self, event):
        """View an eclass file"""
        #TODO: This is a modal dialog, use a wxFrame maybe?
        d = "%s/eclass/" % portdir
        c = os.listdir(d)
        c.sort()
        dlg = wxSingleChoiceDialog(self, 'View an Eclass', 'Eclass',
                                   c, wxOK|wxCANCEL)
        if dlg.ShowModal() == wxID_OK:
            opt = dlg.GetStringSelection()
            file = "%s/%s" % (d, opt)
            msg = open(file, "r").read()
            dlg.Destroy()
            dlg = wxScrolledMessageDialog(self, msg, opt)
            dlg.Show(True)
        else:
            dlg.Destroy()
            return



    def OnMnuPref(self, event):
        """Modify preferences"""
        win = dialogs.Preferences(self, -1, "Preferences", \
                                size=wxSize(350, 200), \
                                style = wxDEFAULT_DIALOG_STYLE \
                                )
        win.CenterOnScreen()
        val = win.ShowModal()
        if val == wxID_OK:
            self.pref['browser'] = win.browser.GetValue()
            self.pref['xterm'] = win.xterm.GetValue()
            self.pref['diff'] = win.diff.GetValue()
            self.pref['editor'] = win.editor.GetValue()
            self.pref['autoTabs'] = win.autoTabs.GetValue()
            self.pref['fileBrowser'] = win.fileBrowser.GetValue()
            self.pref['use'] = win.use.GetValue()
            self.pref['features'] = win.features.GetValue()
            self.pref['log'] = win.log.GetValue()
            f = open(os.path.expanduser('~/.abeni/abenirc'), 'w')
            f.write('browser = %s\n' % self.pref['browser'])
            f.write('xterm = %s\n' % self.pref['xterm'])
            f.write('diff = %s\n' % self.pref['diff'])
            f.write('editor = %s\n' % self.pref['editor'])
            f.write('autoTabs = %s\n' % self.pref['autoTabs'])
            f.write('fileBrowser = %s\n' % self.pref['fileBrowser'])
            f.write('use = %s\n' % self.pref['use'])
            f.write('features = %s\n' % self.pref['features'])
            f.write('log = %s\n' % self.pref['log'])
            f.close()

    def OnMnuAbout(self,event):
        """Obligitory About me and my app screen"""
        msg = 'Abeni %s  is a Python and wxPython application\n' \
              'by Rob Cakebread released under the GPL license.\n\n' % __version__
        title = 'About Abeni %s ' % __version__
        self.MyMessage(msg, title)

    def GetCategory(self):
        """Return category of ebuild"""
        categoryDir = os.path.join (portdir_overlay, self.panelMain.Category.GetValue())
        return categoryDir

    def isDefault(self, var):
        """ Return 1 if varibale is in list of default ebuild variables"""
        for l in defaults:
            if var == l:
                return 1

    def LoadByPackage(self, f):
        """Offer list of ebuilds when given a package or filename on command line"""
        ebuilds = []
        if string.find(f, '/') == -1:
            s = 'etcat -v "^%s$"' % f
        else:
            s = 'etcat -v %s' % f
        for l in os.popen(s).readlines():
            if l[0:9] == '        [':
                l = l.strip()
                l = l[6:]
                ebuilds.append(l)
        if len(ebuilds):
            dlg = wxSingleChoiceDialog(self, 'Choose an ebuild:', 'Ebuilds Available',
                        ebuilds, wxOK|wxCANCEL)
            if dlg.ShowModal() == wxID_OK:
                s = dlg.GetStringSelection()
                s = string.split(s, ' ')
                if len(s) == 3:
                    overlay = 1
                else:
                    overlay = 0
                cat = string.split(s[0], '/')[0]
                package = string.split(s[0], '/')[1]
                if overlay:
                    if string.find(f, '/') == -1:
                        fname = '%s/%s/%s/%s.ebuild' % (portdir_overlay, cat, f, package)
                    else:
                        fname = '%s/%s/%s.ebuild' % (portdir_overlay, f, package)
                else:
                    if string.find(f, '/') == -1:
                        fname = '%s/%s/%s/%s.ebuild' % (portdir, cat, f, package)
                    else:
                        fname = '%s/%s/%s.ebuild' % (portdir, f, package)
                if os.path.exists(fname):
                    LoadEbuild(self, fname, portdir)
                else:
                    print "Error: Can't load %s" % fname
            dlg.Destroy()
        else:
            print "Package " + f + " not found. Be sure to use full package name."

    def GetS(self):
        p = self.GetP()
        e = '%s/portage/%s/temp/environment' % (portage_tmpdir, p)
        if not os.path.exists(e):
            return 0
        f = open(e, 'r')
        l = f.readline()
        while l:
            if l[0:2] == "S=":
                return l[2:].strip()
            l = f.readline()
        #This should never get reached, since there should always be an S:
        return 0

    def OnMnuViewMakefile(self, event):
        """Show Makefile in editor window"""
        #We can't read ${WORKDIR} as non-root, so we have to copy the file and change permissions.
        if not self.editing:
            return
        s = self.GetS()
        if s:
            try:
                os.system('sudo cp %s/Makefile /tmp/Makefile 2> /dev/null' % s)
                os.system('sudo chmod a+r /tmp/Makefile 2> /dev/null')
            except:
                pass
            if os.path.exists('/tmp/Makefile'):
                self.ViewMakefile()
            else:
                msg = 'No Makefile found in %s' % s
                title = 'Error'
                self.MyMessage(msg, title, "error")
        else:
                msg = 'You need to unpack the package first'
                title = 'Error'
                self.MyMessage(msg, title, "error")

    def ViewMakefile(self):
        """Show Makefile in editor window"""
        #We can't read ${WORKDIR} as non-root, so we have to copy the file and change permissions.
        s = self.GetS()
        if s:
            os.system('sudo cp %s/Makefile /tmp/Makefile 2> /dev/null' % s)
            os.system('sudo chmod a+r /tmp/Makefile 2> /dev/null')
            if os.path.exists('/tmp/Makefile'):
                try:
                    self.nb.RemovePage(self.tabs.index('Makefile'))
                    del self.tabs[self.tabs.index('Makefile')]
                except:
                    pass
                self.AddEditor('Makefile', open('/tmp/Makefile', 'r').read())
                os.system('sudo rm /tmp/Makefile')

    def GetEnvs(self):
        #if not self.CheckUnpacked():
            #return
        self.env = {}
        p = self.panelMain.EbuildFile.GetValue()[:-7]
        f = '%s/portage/%s/temp/environment' % (portage_tmpdir, p)
        if not os.path.exists(f):
            cmd = 'sudo /usr/sbin/ebuild %s setup' % self.filename
            self.write(cmd)
            os.system(cmd)
        lines = open(f, 'r').readlines()
        envVars = ['A', 'AA', 'AUTOCLEAN', 'BUILDDIR', 'BUILD_PREFIX', \
                'D', 'DESTTREE', 'EBUILD', 'FEATURES', 'FILESDIR', \
                'INHERITED', 'KV', 'KVERS', 'O', 'P', 'PF', 'PN', 'PV', \
                'PVR', 'RESTRICT', 'S', 'SRC_URI', 'T', 'WORKDIR']
        for l in lines:
            if "=" in l:
                s = string.split(l, '=')
                var = s[0]
                val = s[1]
                if var in envVars:
                    #Is this why A doesn't show up with multipe URI's:
                    self.env[var] = val.strip()

    def OnMnuViewConfigure(self, event):
        """Show configure file in editor window"""
        #We can't read ${WORKDIR} as non-root, so we have to copy the file and change permissions.
        if not self.editing:
            return
        if not self.CheckUnpacked():
            msg = 'You need to unpack the package first'
            title = 'Error'
            self.MyMessage(msg, title, "error")
            return
        s = self.GetS()
        if s:
            try:
                os.system('sudo cp %s/configure /tmp/configure 2> /dev/null' % s)
                os.system('sudo chmod a+r /tmp/configure 2> /dev/null')
            except:
                pass
            # Example: /var/tmp/portage/zinf-2.2.3/work/zinf-2.2.3/configure
            if os.path.exists('/tmp/configure'):
                self.ViewConfigure()
            else:
                msg = 'No "configure" found in %s' % s
                title = 'Error'
                self.MyMessage(msg, title, "error")

    def ViewConfigure(self):
        """Show configure file in editor window"""
        #We can't read ${WORKDIR} as non-root, so we have to copy the file and change permissions.
        s = self.GetS()
        try:
            os.system('sudo cp %s/configure /tmp/configure 2> null' % s)
            os.system('sudo chmod a+r /tmp/configure 2> null')
        except:
            pass
        if os.path.exists('/tmp/configure'):
            try:
                self.nb.RemovePage(self.tabs.index('configure'))
                del self.tabs[self.tabs.index('configure')]
            except:
                pass
            self.AddEditor('configure', open('/tmp/configure', 'r').read())
            os.system('sudo rm /tmp/configure')

    def CheckUnpacked(self):
        p = self.GetP()
        if os.path.exists('%s/portage/%s/.unpacked' % (portage_tmpdir, p)):
            return 1
        else:
            return 0

    def OnMnuCreateDigest(self, event):
        """Run 'ebuild filename digest' on this ebuild"""
        if not self.editing:
            return
        if self.SaveEbuild():
            #TODO: Strip escape codes so we can put in a text widget for those who use sudo
            cmd = 'FEATURES="%s" USE="%s" sudo /usr/sbin/ebuild %s digest' % \
                (self.pref['features'], self.pref['use'], self.filename)
            #os.system(self.pref['xterm'] + ' -T "Creating Digest" -hold -e ' + cmd + ' &')
            self.ExecuteInLog(cmd)

    def OnToolbarUnpack(self, event):
        if self.editing:
            if self.SaveEbuild():
                #self.write("Unpacking %s " % self.filename)
                self.action = 'unpack'
                cmd = 'FEATURES="%s" USE="%s" sudo /usr/sbin/ebuild %s unpack' % \
                    (self.pref['features'], self.pref['use'], self.filename)
                self.ExecuteInLog(cmd)

    def OnToolbarCompile(self, event):
        if self.editing:
            if self.SaveEbuild():
                #self.write("Compiling %s " % self.filename)
                cmd = 'FEATURES="%s" USE="%s" sudo /usr/sbin/ebuild %s compile' % \
                    (self.pref['features'], self.pref['use'], self.filename)
                self.ExecuteInLog(cmd)

    def OnToolbarInstall(self, event):
        if self.editing:
            if self.SaveEbuild():
                #self.write("Installing %s " % self.filename)
                cmd = 'FEATURES="%s" USE="%s" sudo /usr/sbin/ebuild %s install' % \
                    (self.pref['features'], self.pref['use'], self.filename)
                self.ExecuteInLog(cmd)

    def OnMnuViewEnvironment(self, event):
        """Show environment file in editor window"""
        if not self.editing:
            return
        self.ViewEnvironment()

    def ViewEnvironment(self):
        """Show environment file in editor window"""
        #TODO: This is brief version, the commented out line below gives full environment.
        #Add config option to show either, or menu option. Or both.
        self.GetEnvs()
        txt = ''
        keys = self.env.keys()
        keys.sort()
        for k in keys:
            txt += '%s=%s\n' % (k, self.env[k])
        p = self.panelMain.EbuildFile.GetValue()[:-7]
        f = '%s/portage/%s/temp/environment' % (portage_tmpdir, p)
        if os.path.exists(f):
            try:
                self.nb.RemovePage(self.tabs.index('Environment'))
                del self.tabs[self.tabs.index('Environment')]
            except:
                pass
            #self.AddEditor('Environment', open(f, 'r').read())
            self.AddEditor('Environment', txt)

    def SetToNewPage(self):
        self.nb.SetSelection(self.nb.GetPageCount() -1)

    def MyMenu(self):
        #Create menus, setup keyboard accelerators
        # File
        self.menu = menu_file = wxMenu()
        mnuNewID=wxNewId()
        menu_file.Append(mnuNewID, "&New ebuild")
        EVT_MENU(self, mnuNewID, self.OnMnuNew)
        mnuLoadID=wxNewId()
        menu_file.Append(mnuLoadID, "&Load ebuild")
        EVT_MENU(self, mnuLoadID, self.OnMnuLoad)
        mnuSaveID=wxNewId()
        menu_file.Append(mnuSaveID, "&Save ebuild")
        EVT_MENU(self, mnuSaveID, self.OnMnuSave)
        mnuExitID=wxNewId()
        menu_file.Append(mnuExitID, "E&xit\tAlt-X")
        EVT_MENU(self, mnuExitID, self.OnMnuExit)
        menubar = wxMenuBar()
        menubar.Append(menu_file, "&File")
        EVT_MENU_RANGE(self, wxID_FILE1, wxID_FILE9, self.OnFileHistory)
        self.filehistory = wxFileHistory()
        self.filehistory.UseMenu(self.menu)

        # Variable
        menu_variable = wxMenu()
        mnuNewVariableID = wxNewId()
        menu_variable.Append(mnuNewVariableID, "&New Variable\tF2", "New Variable")
        EVT_MENU(self, mnuNewVariableID, self.OnMnuNewVariable)
        mnuDelVariableID = wxNewId()
        menu_variable.Append(mnuDelVariableID, "&Delete Variable")
        EVT_MENU(self, mnuDelVariableID, self.OnMnuDelVariable)
        menubar.Append(menu_variable, "&Variable")
        # Function
        menu_function = wxMenu()
        mnuNewFunctionID = wxNewId()
        menu_function.Append(mnuNewFunctionID, "&New Function\tF3", "New Function")
        EVT_MENU(self, mnuNewFunctionID, self.OnMnuNewFunction)
        mnuDelFunctionID = wxNewId()
        menu_function.Append(mnuDelFunctionID, "&Delete Function")
        EVT_MENU(self, mnuDelFunctionID, self.OnMnuDelFunction)
        menubar.Append(menu_function, "Functio&n")
        # Eclass
        menu_eclass = wxMenu()

        mnuGamesID = wxNewId()
        menu_eclass.Append(mnuGamesID, "games")
        EVT_MENU(self, mnuGamesID, self.OnMnuEclassGames)

        mnuCVSID = wxNewId()
        menu_eclass.Append(mnuCVSID, "cvs")
        EVT_MENU(self, mnuCVSID, self.OnMnuEclassCVS)

        mnuDistutilsID = wxNewId()
        menu_eclass.Append(mnuDistutilsID, "distutils")
        EVT_MENU(self, mnuDistutilsID, self.OnMnuEclassDistutils)

        menubar.Append(menu_eclass, "E&class")
        # Tools
        menu_tools = wxMenu()
        mnuEbuildID = wxNewId()
        menu_tools.Append(mnuEbuildID, "Run &ebuild <this ebuild> <command>\tf4")
        EVT_MENU(self, mnuEbuildID, self.OnMnuEbuild)
        mnuEmergeID = wxNewId()
        menu_tools.Append(mnuEmergeID, "Run e&merge <args> <this ebuild>\tf5")
        EVT_MENU(self, mnuEmergeID, self.OnMnuEmerge)
        mnuLintoolID = wxNewId()

        mnuGetDepsID = wxNewId()
        menu_tools.Append(mnuGetDepsID, "Get deps for this ebuild")
        EVT_MENU(self, mnuGetDepsID, self.OnMnuGetDeps)
        mnuGetDepsID = wxNewId()

        menu_tools.Append(mnuLintoolID, "Run &Lintool on this ebuild")
        EVT_MENU(self, mnuLintoolID, self.OnMnuLintool)
        mnuRepomanID = wxNewId()
        menu_tools.Append(mnuRepomanID, "Run &Repoman on this ebuild")
        EVT_MENU(self, mnuRepomanID, self.OnMnuRepoman)
        mnuDigestID = wxNewId()
        menu_tools.Append(mnuDigestID, "&Create Digest")
        EVT_MENU(self, mnuDigestID, self.OnMnuCreateDigest)
        mnuDiffCreateID = wxNewId()
        menu_tools.Append(mnuDiffCreateID, "Create diff &file")
        EVT_MENU(self, mnuDiffCreateID, self.OnMnuDiffCreate)

        mnuClearLogID = wxNewId()
        menu_tools.Append(mnuClearLogID, "Clear log &window\tf11")
        EVT_MENU(self, mnuClearLogID, self.OnMnuClearLog)
        menubar.Append(menu_tools, "&Tools")

        # Project
        menu_proj = wxMenu()

        mnuBugID = wxNewId()
        menu_proj.Append(mnuBugID, "Enter or view info")
        EVT_MENU(self, mnuBugID, self.OnMnuBugzilla)

        mnuSumID = wxNewId()
        menu_proj.Append(mnuSumID, "Summarize all overlay ebuilds")
        EVT_MENU(self, mnuSumID, self.OnMnuBugzSum)

        menubar.Append(menu_proj, "&Project")

        # View
        menu_view = wxMenu()
        mnuViewID = wxNewId()
        menu_view.Append(mnuViewID, "en&vironment")
        EVT_MENU(self, mnuViewID, self.OnMnuViewEnvironment)
        mnuViewConfigureID = wxNewId()
        menu_view.Append(mnuViewConfigureID, "configure")
        EVT_MENU(self, mnuViewConfigureID, self.OnMnuViewConfigure)
        mnuViewMakefileID = wxNewId()
        menu_view.Append(mnuViewMakefileID, "Makefile")
        EVT_MENU(self, mnuViewMakefileID, self.OnMnuViewMakefile)
        mnuDiffID = wxNewId()
        menu_view.Append(mnuDiffID, "&diff")
        EVT_MENU(self, mnuDiffID, self.OnMnuDiff)
        mnuEditID = wxNewId()
        menu_view.Append(mnuEditID, "This ebuild in e&xternal editor\tf7")
        EVT_MENU(self, mnuEditID, self.OnMnuEdit)
        #mnuExploreWorkdirID = wxNewId()
        #menu_view.Append(mnuExploreWorkdirID, "File browser in ${WORKDIR}")
        #EVT_MENU(self, mnuExploreWorkdirID, self.ExploreWorkdir)
        menubar.Append(menu_view, "Vie&w")
        # Options
        self.menu_options = wxMenu()
        mnuPrefID = wxNewId()
        self.menu_options.Append(mnuPrefID, "&Global Preferences")
        EVT_MENU(self, mnuPrefID, self.OnMnuPref)
        self.menu_options.AppendSeparator()
        self.mnuLogBottomID = wxNewId()
        self.menu_options.Append(self.mnuLogBottomID, "Log at &bottom\tf9", "", wxITEM_RADIO)
        EVT_MENU(self, self.mnuLogBottomID, self.OnMnuLogBottom)
        self.mnuLogWindowID = wxNewId()
        self.menu_options.Append(self.mnuLogWindowID, "Log in separate &window\tf10", "", wxITEM_RADIO)
        EVT_MENU(self, self.mnuLogWindowID, self.OnMnuLogWindow)
        self.menu_options.AppendSeparator()

        menubar.Append(self.menu_options, "&Options")
        # Help
        menu_help = wxMenu()
        mnuHelpID = wxNewId()
        menu_help.Append(mnuHelpID,"&Contents\tF1")
        EVT_MENU(self, mnuHelpID, self.OnMnuHelp)
        mnuHelpRefID = wxNewId()
        menu_help.Append(mnuHelpRefID,"&Ebuild Quick Reference")
        EVT_MENU(self, mnuHelpRefID, self.OnMnuHelpRef)
        mnuEclassID = wxNewId()
        menu_help.Append(mnuEclassID, "&View eclass files")
        EVT_MENU(self, mnuEclassID, self.OnMnuEclassHelp)
        mnuUseID = wxNewId()
        menu_help.Append(mnuUseID, "View &USE descriptions")
        EVT_MENU(self, mnuUseID, self.OnMnuUseHelp)
        mnuAboutID = wxNewId()
        menu_help.Append(mnuAboutID,"&About")
        EVT_MENU(self, mnuAboutID, self.OnMnuAbout)
        menubar.Append(menu_help,"&Help")
        self.SetMenuBar(menubar)


class MyLog(wxPyLog):
    def __init__(self, textCtrl, logTime=0):
        wxPyLog.__init__(self)
        self.tc = textCtrl
        self.logTime = logTime

    def DoLogString(self, message, timeStamp):
        if self.logTime:
            message = time.strftime("%X", time.localtime(timeStamp)) + \
                      ": " + message
        if self.tc:
            self.tc.AppendText(message + '\n')

class MyApp(wxPySimpleApp):

    """ Main wxPython app class """

    def OnInit(self):
        """Set up the main frame"""
        # Enable gif, jpg, bmp, png handling for wxHtml and icons
        wxInitAllImageHandlers()
        frame=MyFrame(None, -1, 'Abeni - The ebuild Builder ' + __version__)
        frame.Show(true)
        self.SetTopWindow(frame)
        return true

app=MyApp(0)
app.MainLoop()

