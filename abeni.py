#!/usr/bin/env python

"""Abeni - Gentoo Linux Ebuild Editor/Syntax Checker
Released under the terms of the GNU Public License v2"""

__author__ = 'Rob Cakebread'
__email__ = 'robc@myrealbox.com'
__version__ = '0.0.5'
__changelog_ = 'http://abeni.sf.net/ChangeLog'

print "Importing portage config, wxPython, Python and Abeni modules..."
from portage import config
from wxPython.wx import *
from wxPython.lib.dialogs import wxScrolledMessageDialog
import os, string, sys, urlparse
import dialogs, panels
from utils import *

#Get portage path locations from /etc/make.conf
distdir = config().environ()['DISTDIR']
portdir = config().environ()['PORTDIR']
portdir_overlay = config().environ()['PORTDIR_OVERLAY']
portage_tmpdir = config().environ()['PORTAGE_TMPDIR']

defaults = ["SRC_URI", "HOMEPAGE", "DEPEND", "RDEPEND", "DESCRIPTION", \
            "S", "IUSE", "SLOT", "KEYWORDS", "LICENSE"]

class MyFrame(wxFrame):

    """ Main frame that holds the menu, toolbar and notebook """

    def __init__(self, parent, id, title):
        wxFrame.__init__(self, parent, -1, title, size=wxSize(900,600))
        #self.SetAutoLayout(true)
        #Catch the close event so we can clean up nicely.
        EVT_CLOSE(self,self.OnClose)
        # Are we in the process of editing an ebuild?
        self.editing = 0
        #Load recently accessed ebuilds
        if not os.path.exists(os.path.expanduser('~/.abeni')):
            print "Creating directory " + os.path.expanduser('~/.abeni')
            os.mkdir(os.path.expanduser('~/.abeni'))
        bookmarks = os.path.expanduser('~/.abeni/recent.txt')
        if os.path.exists(bookmarks):
            self.recentList = open(bookmarks, 'r').readlines()
        else:
            self.recentList = []
        # Get options from ~/.abeni/abenirc file
        GetOptions(self)
        # Custom functions added instances
        self.funcList = []
        #Misc editor tab instances
        self.editorList = []
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
        # Saved-state
        self.saved = 1
        #Stuff to keep log window updating in "real-time" as shell commands are executed
        self.process = None
        ID_Timer = wxNewId()
        #self.processTimer = wxTimer(self, ID_Timer)
        #EVT_TIMER(self, ID_Timer, self.OnTimer)
        EVT_IDLE(self, self.OnIdle)
        self.inp = None
        #EVT_END_PROCESS(self, -1, self.OnProcessEnded)
        #application icon 16x16
        iconFile = ('/usr/share/pixmaps/abeni/abeni_logo16.png')
        icon = wxIcon(iconFile, wxBITMAP_TYPE_PNG)
        self.SetIcon(icon)
        AddMenu(self)
        AddToolbar(self)
        self.sb = self.CreateStatusBar(1, wxST_SIZEGRIP)
        splitter = wxSplitterWindow(self, -1, style=wxNO_3D|wxSP_3D)
        def EmptyHandler(evt): pass
        EVT_ERASE_BACKGROUND(splitter, EmptyHandler)
        self.nb = wxNotebook(splitter, -1, style=wxCLIP_CHILDREN)
        self.log = wxTextCtrl(splitter, -1,
                             style = wxTE_MULTILINE|wxTE_READONLY|wxHSCROLL)
        wxLog_SetActiveTarget(MyLog(self.log))
        self.Show(True)
        splitter.SplitHorizontally(self.nb, self.log, 400)
        splitter.SetMinimumPaneSize(20)
        #Load ebuild if specified on command line, by filename or by full package name
        if len(sys.argv) == 2:
            f = sys.argv[1]
            try:
                os.path.exists(f)
                LoadEbuild(self, f, __version__, portdir)
            except:
                print "No such file: " + f
                print "Checking for package: " + f
                self.LoadByPackage(f)

    def Cleanup(self, *args):
        """Cleanup for filehistory"""
        pass
        # No idea why this is used. It was in the demo code. It breaks in wxPython 2.4.2.1
        # because object doesn't exist after notebook is removed then added.
        #del self.filehistory

    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wxLogMessage(text)

    def write(self, txt):
        self.WriteText(txt)

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
        t += (command + "\n")
        self.panelMain.stext.SetValue(t)

    def OnMnuEdit(self, event):
        """Launch external editor then reload ebuild after editor exits"""
        if self.editing:
            if not self.VerifySaved():
                self.ClearNotebook()
                #Don't run sudo, we want user owner/perms on ebuild files in PORTDIR_OVERLAY
                os.system('%s %s' % (self.pref['editor'], self.filename))
                LoadEbuild(self, self.filename, __version__, portdir)

    def OnMnuDiff(self, event):
        """Run diff program on original vs. saved ebuild"""
        #TODO Add error dialog if last opened wasn't same package, or is empty
        if not self.editing:
            return

        #orgFile = string.replace(self.filename, 'local/', '')
        if self.lastFile:
            os.system(self.pref['diff'] + ' ' + self.lastFile + ' ' + self.filename + ' &')

    def OnMnuDiffCreate(self, event):
        """Create diff file of original vs. saved ebuild"""
        #TODO: Add error dialog if last opened wasn't same package, or is empty
        # Add dialog telling them file is saved in ~/.abeni/diffFile
        if not self.editing:
            return

        #No file to compare with
        if not self.lastFile:
            return

        #orgFile = string.replace(self.filename, 'local/', '')
        diffFile = string.replace(self.ebuild_file, '.ebuild', '.diff')
        #print orgFile, diffFile
        cmd = 'diff -u %s %s > ~/.abeni/%s' % (self.lastFile, self.filename, diffFile)
        #os.system(cmd)
        self.ExecuteInLog(cmd)

    def OnMnuCreateDigest(self, event):
        """Run 'ebuild filename digest' on this ebuild"""
        if not self.editing:
            return
        WriteEbuild(self)
        # I did this in an xterm because we need to be root and it has colored output.
        #TODO: Strip escape codes so we can put in a text widget for those who use sudo
        cmd = 'sudo /usr/sbin/ebuild %s digest' % self.filename
        #os.system(self.pref['xterm'] + ' -T "Creating Digest" -hold -e ' + cmd + ' &')
        self.ExecuteInLog(cmd)

    def OnMnuRepoman(self, event):
        """Run 'repoman-local-5.py' on this ebuild"""
        if not self.editing:
            return
        d = os.getcwd()
        os.chdir(self.ebuildDir)
        cmd = '"/usr/bin/repoman-safe.py ; echo Press ENTER ; read foo"'
        #cmd2 = self.pref['xterm'] + ' -T "repoman-safe" -e ' + cmd + ' &'
        #os.system(cmd2)
        #os.chdir(d)
        self.ExecuteInLog(cmd)


    def OnMnuEmerge(self, event):
        """Run 'emerge <options> <this ebuild>' """
        if not self.editing:
            return
        WriteEbuild(self)
        dlg = wxTextEntryDialog(self, 'What arguments do you want to pass?',
                            'Arguments?', '')
        dlg.SetValue("")
        if dlg.ShowModal() == wxID_OK:
            opts = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        if opts == '-p' or opts == '--pretend':
            #cmd = '"/usr/bin/emerge ' + opts + ' ' + self.filename + ' ; echo Done"'
            cmd = '/usr/bin/emerge %s %s' % (opts, self.filename)
        else:
            if opts == 'unmerge' or opts == '-C':
                #cmd = 'sudo /usr/bin/emerge ' + opts + ' ' + self.package + ' ; echo Done'
                cmd = 'sudo /usr/bin/emerge %s %s' % (opts, self.package)
                print cmd
            else:
                #cmd = 'sudo /usr/bin/emerge ' + opts + ' ' + self.filename + ' ; echo Done'
                cmd = 'sudo /usr/bin/emerge %s %s' % (opts, self.filename)
        #cmd2 = self.pref['xterm'] + ' -T "emerge" -hold -e ' + cmd + ' &'
        #os.system(cmd2)
        self.ExecuteInLog(cmd)


    def OnMnuEbuild(self, event):
        """Run 'ebuild <file> <cmd>' """
        if not self.editing:
            return
        WriteEbuild(self)
        c = ['setup', 'depend', 'merge', 'qmerge', 'unpack',
             'compile', 'rpm', 'package', 'prerm', 'postrm',
             'preinst', 'postinst', 'config', 'touch', 'clean',
             'fetch', 'digest', 'install', 'unmerge']
        c.sort()
        dlg = wxSingleChoiceDialog(self, 'Command:', 'Choose ebuild command',
                                   c, wxOK|wxCANCEL)
        if dlg.ShowModal() == wxID_OK:
            opt = dlg.GetStringSelection()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        #cmd = 'sudo /usr/sbin/ebuild ' + self.filename + ' ' + opt + ' ; echo Done'
        cmd = 'sudo /usr/sbin/ebuild %s %s' % (self.filename, opt)
        #cmd2 = '%s  -T "ebuild" -hold -e %s' % (self.pref['xterm'], cmd)
        #os.system(cmd2)
        #for l in os.popen(cmd).readline():
        #    self.write(l)
        self.ExecuteInLog(cmd)

    def OnIdle(self, event):
        if self.inp is not None:
            l = self.inp.readline()
            self.write(l)
            while l:
                l = self.inp.readline()
                self.write(l)
            self.inp = None
            self.tb.Enable(True)
            self.tb.EnableTool(self.toolStopID, False)
            self.nb.Enable(True)
            #self.menu.Enable(True)

    def ExecuteInLog(self, cmd):
        """Executes cmd and shows output asynchronously in log window"""
        self.tb.EnableTool(self.toolStopID, True)
        self.nb.Enable(False)
        #self.menu.Enable(False)
        self.tb.Enable(False)
        wxSafeYield()
        sys.stdout.write("\n")
        sys.stdout.flush()
        self.inp = os.popen('FEATURES="noauto" %s 2>&1 &' % cmd)
        l = self.inp.readline()
        self.write(l)


    def OnMnuLintool(self, event):
        """Run 'lintool' on this ebuild"""
        if not self.editing:
            return

        cmd = '/usr/bin/lintool %s' % self.filename
        #print cmd
        #cmd2 = self.pref['xterm'] + ' -T "Lintool" -e ' + cmd + ' &'
        #print cmd2
        #os.system(cmd2)
        self.ExecuteInLog(cmd)

    def ClearNotebook(self):
        """Delete all pages in the notebook"""
        self.nb.DeleteAllPages()
        self.funcList = []
        self.statementList = []
        self.editorList = []
        self.funcOrder = []
        self.varOrder = []

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
            LoadEbuild(self, path, __version__, portdir)
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
                    LoadEbuild(self, filename, __version__, portdir)
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

    def OnToolZone(self, event):
        """Clear statusbar 3 seconds after mouse moves over toolbar icon
        if self.timer is None:
            self.timer = wxTimer(self)
        if self.timer.IsRunning():
            self.timer.Stop()
        self.timer.Start(4000)
        """
        event.Skip()

    def OnClearSB(self, event):
        """OnToolZone clear status bar after hovering over toolbar icon"""
        #self.timer.Stop()
        #self.timer = None
        self.sb.SetStatusText("", 0)

    def OnPageChanged(self, event):
        """Catch event when page in notebook is changed"""
        self.nbPage = event.GetSelection()
        event.Skip()

    def OnMnuEclassCVS(self, event):
        """Add Python distutils-related variables, inherit etc."""
        if not self.editing:
            return
        EclassCVS(self)

    def OnMnuEclassDistutils(self, event):
        """Add CVS-related variables, inherit etc."""
        if not self.editing:
            return
        EclassDistutils(self)

    def OnMnuNewFunction(self, event):
        """Dialog to add new function"""
        if not self.editing:
            return
        from NewFuncDialog import wxDialog1
        dlg = wxDialog1(self)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wxID_OK:
            func, val = dlg.GetFunc()
            self.AddFunc(func, val)
        self.saved = 0
        dlg.Destroy()

    def AddFunc(self, newFunction, val):
        """Add page in notebook for a new function"""
        n = panels.NewFunction(self.nb, self.sb, self.pref)
        if newFunction != 'Original File':
            self.funcList.append(n)
        self.nb.AddPage(n, newFunction)
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
                x,y  = self.GetSize()
                self.SetSize(wxSize(x+1, y))
                break
            n += 1
        del self.funcList[n]
        self.saved = 0
        #Neither of these fix the bug where the tab still shows. If you resize the window, it deletes it.
        #self.nb.Refresh(true)
        #self.Refresh()

    def AddEditor(self, name, val):
        """Add page in notebook for an editor"""
        n = panels.Editor(self.nb, self.sb, self.pref)
        self.editorList.append(n)
        self.nb.AddPage(n, name)
        n.editorCtrl.SetText(val)
        #self.nb.SetSelection(self.nb.GetPageCount() -1)

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
        msg = self.checkEntries()
        if not msg:
            defaultVars = getDefaultVars(self)
            WriteEbuild(self)
            self.saved = 1
        else:
            dlg = wxMessageDialog(self, msg, 'Abeni: Error Saving', wxOK | wxICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def checkEntries(self):
        """Validate entries on forms"""
        category = self.panelMain.Category.GetValue()
        categoryDir = self.GetCategory()
        valid_cat = os.path.join(portdir, category)
        if categoryDir == portdir_overlay + '/':
            msg = "You must specify a category."
            return msg
        if not os.path.exists(valid_cat):
            msg = category + " isn't a valid category."
            return msg

        return 0

    def OnMnuNew(self,event):
        """Creates a new ebuild from scratch"""
        #TODO: Add an "Are you sure?" dialog
        # Show dialog if URI isn't properly formed or can't determine package, filename, ebuild name
        if self.editing:
            win = dialogs.GetURIDialog(self, -1, "Enter Package URI", \
                                size=wxSize(350, 200), \
                                style = wxDEFAULT_DIALOG_STYLE \
                                )
            win.CenterOnScreen()
            val = win.ShowModal()
            self.URI = win.URI.GetValue()
            if self.URI == 'http://' or self.URI == '':
                return
            if self.URI == "CVS" or self.URI == "cvs":
                self.URI = "package-cvs-0.0.1"
            if val == wxID_OK and self.URI:
                self.ClearNotebook()
                self.AddPages()
                self.panelMain.PopulateDefault()
                self.panelMain.SetURI(self.URI)
                self.panelMain.SetName(self.URI)
                self.panelMain.SetPackage()
                self.panelChangelog.Populate(filename= portdir + '/skel.ChangeLog')
                self.editing = 1
                if self.URI == "CVS" or self.URI == "cvs":
                    self.OnMnuEclassCVS(-1)
                self.SetTitle(self.panelMain.GetEbuildName() + " | Abeni " + __version__)

    def AddPages(self):
        """Add pages to blank notebook"""
        self.panelMain=panels.main(self.nb, self.sb, self.pref)
        self.panelDepend=panels.depend(self.nb, self.sb, self.pref)
        self.panelChangelog=panels.changelog(self.nb, self.sb, self.pref)
        self.nb.AddPage(self.panelMain, "Main")
        self.nb.AddPage(self.panelDepend, "Dependencies")
        self.nb.AddPage(self.panelChangelog, "ChangeLog")

    def OnClose(self, event):
        """Called when trying to close application"""
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

    def OnMnuPref(self, event):
        """Global preferences entry dialog"""
        import OptionFrame
        dlg = OptionFrame.OptionFrame(None, -1, "Global Preferences")
        dlg.Show(true)

    def OnMnuAbout(self,event):
        """Obligitory About me and my app screen"""
        dlg = wxMessageDialog(self, 'Abeni ' + __version__ + ' is a Python and wxPython application\n' +
                                'by Rob Cakebread released under the GPL license.\n\n', \
                                'About Abeni ' + __version__, wxOK | wxICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

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
        ebuilds = []
        for l in os.popen('etcat -v ' + '"^' + f + '$"').readlines():
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
                    fname = portdir_overlay + '/' + cat + '/' + f + '/' + package + '.ebuild'
                else:
                    fname = portdir + '/' + cat + '/' + f + '/' + package + '.ebuild'
                try:
                    os.path.exists(fname)
                    LoadEbuild(self, fname, __version__, portdir)
                except:
                    self.write("Error: Can't load %s") % fname
            dlg.Destroy()
        else:
            print "Package " + f + " not found. Be sure to use full package name."

    def ViewEnvironment(self, event):
        """Unpack source and show environment in editor window"""
        if not self.editing:
            return
        WriteEbuild(self)
        pv = self.panelMain.EbuildFile.GetValue()[:-7]
        f = '%s/portage/%s/temp/environment' % (portage_tmpdir, pv)
        if not os.path.exists(f):
            cmd = 'sudo /usr/sbin/ebuild %s unpack' % self.filename
            #os.system('%s -T "Unpack" -hold -e %s' % (self.pref['xterm'], cmd))
            self.ExecuteInLog(cmd)
        # Example: /var/tmp/portage/pysnmp-2.0.8/temp/environment
        # Crud. Have to wait till above finishes.
        if os.path.exists(f):
            self.AddEditor('Environment', open(f, 'r').read())
            self.SetToNewPage()
        else:
            self.write("No enviornment: %s" % f)

    def SetToNewPage(self):
        self.nb.SetSelection(self.nb.GetPageCount() -1)

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
