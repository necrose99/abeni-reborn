import os
import urlparse
import string

from wxPython.lib.dialogs import wxScrolledMessageDialog
from wxPython.wx import *
from portage import config, settings, pkgsplit

import utils
import dialogs
import abeniCVS
import __version__ 

env = config(clone=settings).environ()
portdir_overlay = env['PORTDIR_OVERLAY'].split(" ")[0]
if portdir_overlay[-1] == "/":
    portdir_overlay = portdir_overlay[:-1]
portdir = env['PORTDIR']
portage_tmpdir = env['PORTAGE_TMPDIR']


class MyFrame(wxFrame):

    """ Main frame that holds the menu, toolbar and notebook """

    def __init__(self, parent, id, title):
        wxFrame.__init__(self, parent, -1, title, size=wxSize(900,720))
        if os.getuid() != 0:
            utils.MyMessage(self, "You must be root, or running Abeni with 'sudo'.",\
                           "You must be root.", "error")
            sys.exit(1)
        # Are we in the process of editing an ebuild?
        self.editing = 0
        abeniDir = os.path.expanduser('~/.abeni')
        if not os.path.exists(abeniDir):
            os.mkdir(abeniDir)
        bugzDir = '%s/bugz' % abeniDir
        if not os.path.exists(bugzDir):
            os.mkdir(bugzDir)
        templatesDir = '%s/templates' % abeniDir
        if not os.path.exists(templatesDir):
            os.mkdir(templatesDir)
            shutil.copy("/usr/share/abeni/templates", \
             ("%s/templates/Templates.py" % abeniDir))
        sys.path.append(templatesDir)
        rcfile = '%s/abenirc' % abeniDir
        if not os.path.exists(rcfile):
            shutil.copy("/usr/share/abeni/abenirc", rcfile)
        #Load recently accessed ebuilds
        bookmarks = '%s/recent.txt' % abeniDir
        if os.path.exists(bookmarks):
            self.recentList = open(bookmarks, 'r').readlines()
        else:
            self.recentList = []
        # Get options from ~/.abeni/abenirc file
        utils.GetOptions(self)
        # Custom functions added instances
        self.funcList = []
        #Misc statements/commands instances
        self.statementList = []
        # Keep track of order variables are set
        self.varOrder = []
        # Keep track of order functions are set
        self.funcOrder = []
        # ${S}
        self.s = ''
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
        # CVS ebuild?
        self.CVS = None
        # Ordered list of notebook tabs
        self.tabs = []
        self.tabsInstance = []
        #Stuff to keep log window updating in "real-time" as shell commands
        # are executed
        self.process = None
        # Setting for noauto toggle button
        utils.StripNoAuto(self)
        self.noauto = 1
        #application icon 16x16
        iconFile = ('/usr/share/pixmaps/abeni/abeni_logo16.png')
        icon = wxIcon(iconFile, wxBITMAP_TYPE_PNG)
        self.SetIcon(icon)
        self.MyMenu()
        utils.AddToolbar(self)
        self.sb = self.CreateStatusBar(2, wxST_SIZEGRIP)
        self.splitter = wxSplitterWindow(self, -1, style=wxNO_3D|wxSP_3D)


        self.nb = wxNotebook(self.splitter, -1, style=wxCLIP_CHILDREN)
        self.nb.portdir_overlay = portdir_overlay
        self.nb.portdir = portdir
        EVT_NOTEBOOK_PAGE_CHANGED(self.nb, -1, self.OnPageChanged)
        EVT_NOTEBOOK_PAGE_CHANGED(self.nb, -1, self.OnPageChanging)
        EVT_CLOSE(self, self.OnClose)
        EVT_END_PROCESS(self, -1, self.OnProcessEnded)
        #def EmptyHandler(evt): pass
        #EVT_ERASE_BACKGROUND(self.splitter, EmptyHandler)
        self.log = wxTextCtrl(self.splitter, -1,
            style = wxTE_MULTILINE|wxTE_READONLY|wxTE_RICH)
            #style = wxTE_MULTILINE|wxTE_READONLY|wxHSCROLL|wxTE_RICH)
        self.log.SetFont(wxFont(12, wxMODERN, wxNORMAL, wxNORMAL, \
            faceName="Andale Mono"))
        #self.log.SetAutoLayout(TRUE)
        #self.log.SetBackgroundColour(wxBLACK)
        #self.log.SetDefaultStyle(wxTextAttr(wxWHITE))
        #self.log.SetDefaultStyle(wxTextAttr(wxNullColour, wxBLACK))
        wxLog_SetActiveTarget(MyLog(self.log))
        self.Show(True)
        self.splitter.SplitHorizontally(self.nb, self.log, 400)
        self.sashPosition = 400
        utils.write(self, " *  PORTDIR=%s" % portdir)
        utils.write(self, " *  PORTDIR_OVERLAY=%s" % portdir_overlay)
        EVT_MENU_RANGE(self, wxID_FILE1, wxID_FILE9, self.OnFileHistory)
        EVT_IDLE(self, self.OnIdle)
        #Load ebuild if specified on command line, by filename or by
        # full package name
        if len(sys.argv) == 2:
            f = sys.argv[1]
            if os.path.exists(f):
                utils.LoadEbuild(self, f, portdir)
            else:
                print "No such file: %s" % f
                print "Checking for package: %s" % f
                #Make sure GUI is drawn before we start the slow search
                wxSafeYield()
                utils.LoadByPackage(self, f)


    def OnTimer(self, evt):
        """Call idle handler every second to update log window"""
        self.HandleIdle()

    def OnIdle(self, event):
        """Called after the GUI stops being idle (mouse or key events)"""
        self.HandleIdle()

    def HandleIdle(self):
        if self.process is not None:
            stream = self.process.GetInputStream()
            if stream.CanRead():
                t = stream.readline()
                utils.write(self, t)

    def OnFileHistory(self, event):
        """Load ebuild on FileHistory event"""
        # get the file based on the menu ID
        fileNum = event.GetId() - wxID_FILE1
        path = self.filehistory.GetHistoryFile(fileNum)
        if not utils.VerifySaved(self):
            utils.ClearNotebook(self)
            utils.LoadEbuild(self, path, portdir)
            # add it back to the history so it will be moved up the list
            self.filehistory.AddFileToHistory(path)

    def OnMnuLoad(self, event):
        """Load ebuild file"""
        if not utils.VerifySaved(self):
            wildcard = "ebuild files (*.ebuild)|*.ebuild"
            dlg = wxFileDialog(self, "Choose a file", portdir, "", \
                                wildcard, wxOPEN)
            if dlg.ShowModal() == wxID_OK:
                filename = dlg.GetPath()
                if self.editing:
                    utils.ClearNotebook(self)
                utils.LoadEbuild(self, filename, portdir)
                self.filehistory.AddFileToHistory(filename)
            dlg.Destroy()

    def __del__(self):
        if self.process is not None:
            self.process.Detach()
            self.process.CloseOutput()
            self.process = None

    def OnMnuLogWindow(self, event):
        """Switch ouput log to separate window"""
        if not self.editing or self.pref['log'] == 'window':
            return
        utils.LogWindow(self)

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

    def OnMnuProjManager(self, event):
        """Open Project Menu self"""
        import ProjectManager
        pself = ProjectManager.MyFrame(self)
        pself.Show(true)

    def OnMnuGetDeps(self, event):
        """Resolve 'lazy' dependencies to full version"""
        # i.e. dev-lang/python TO >=dev-lang/python-2.2.2
        #DEPEND
        l = self.panelDepend.elb1.GetStrings()
        new = self.ResolveDeps(l)
        self.panelDepend.elb1.SetStrings(new)
        #RDEPEND
        l = self.panelDepend.elb2.GetStrings()
        new = self.ResolveDeps(l)

        self.panelDepend.elb2.SetStrings(new)

    def OnMnuDelFunction(self, event):
        """Remove current function page"""
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
        try:
            del self.funcList[n]
        except:
            utils.write(self, "ERROR: Select the function first, then delete it.")
        self.saved = 0

    def OnMnuHelpRef(self, event):
        """Display html help file"""
        if self.pref['browser']:
            os.system(self.pref['browser'] + \
              " 'http://abeni.sf.net/docs/ebuild-quick-reference.html' &")
        else:
            utils.MyMessage(self, "You need to define a browser in preferences.", \
              "Error", "error")

    def OnMnuHelp(self, event):
        """Display html help file"""
        if self.pref['browser']:
            os.system(self.pref['browser'] + \
              " 'http://abeni.sf.net/docs/index.html' &")
        else:
            utils.MyMessage(self, "You need to define a browser in preferences.", \
              "Error", "error")

    def OnMnuSave(self, event):
        """Save ebuild file to disk"""
        if not self.editing:
            return
        utils.SaveEbuild(self)

    def OnMnuNew(self,event):
        """Creates a new ebuild from scratch"""
        if not utils.VerifySaved(self):
            win = dialogs.GetURIDialog(self, -1, "Enter Package URI", \
                                size=wxSize(350, 200), \
                                style = wxDEFAULT_DIALOG_STYLE \
                                )
            win.CenterOnScreen()
            val = win.ShowModal()
            self.URI = win.URI.GetValue()
            if val == wxID_OK:
                utils.ClearNotebook(self)
                utils.AddPages(self)
                utils.AddEditor(self, "Output", "")
                if self.pref['log'] == 'window':
                    utils.LogWindow()
                self.panelMain.PopulateDefault()
                # In case we edit SRC_URI and forget what the
                # original url is:
                utils.write(self, self.URI)
                self.panelMain.SetURI(self.URI)
                self.panelMain.SetName(self.URI)
                self.panelMain.SetPackageName()
                n = pkgsplit(self.panelMain.GetPackage())
                if n:
                    p = ("%s-%s" % (n[0], n[1]))
                    new_uri = self.URI.replace(p, "${P}")
                    self.panelMain.URI.SetValue(new_uri)
                else:
                    self.panelMain.Package.SetValue("")
                    self.panelMain.EbuildFile.SetValue("")
                #self.panelChangelog.Populate("%s/skel.ChangeLog" % portdir, \
                #  portdir)
                if self.URI.find('sourceforge') != -1:
                    a = urlparse.urlparse(self.URI)
                    if a[2].find('sourceforge') != -1:
                        self.panelMain.SetURI('mirror:/%s' % a[2])
                        #This is in case we want to automatically set the 
                        #SourceForge homepage:self.panelMain.Homepage.SetValue(
                        #'"http://sourceforge.net/projects/%s"' % \
                        #self.panelMain.GetPackageName().lower())
                self.editing = 1
                self.saved = 0
                utils.DoTitle(self)

    def OnClose(self, event):
        """Called when trying to close application"""
        #TODO: Give yes/no quit dialog.
        if self.running:
            utils.write(self, "You're executing %s" % self.running)
            return

        if not utils.VerifySaved(self):
            bookmarks = os.path.expanduser('~/.abeni/recent.txt')
            f = open(bookmarks, 'w')
            n = self.filehistory.GetNoHistoryFiles()
            for e in range(n):
                f.write(self.filehistory.GetHistoryFile(e) + '\n')
            f.close()
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

    #TODO: Hmmm. I see a pattern here...
    def OnMnuCreateDigest(self, event):
        """Run 'ebuild filename digest' on this ebuild"""
        if not self.editing:
            return
        if utils.SaveEbuild(self):
            cmd = 'FEATURES="%s" USE="%s" /usr/sbin/ebuild %s digest' % \
                (self.pref['features'], self.pref['use'], self.filename)
            utils.ExecuteInLog(self, cmd)

    def OnToolbarEdit(self, event):
        self.OnMnuEdit()

    def OnToolbarUnpack(self, event):
        if self.editing:
            if utils.SaveEbuild(self):
                self.action = 'unpack'
                cmd = 'FEATURES="%s" USE="%s" /usr/sbin/ebuild %s unpack' % \
                    (self.pref['features'], self.pref['use'], self.filename)
                utils.ExecuteInLog(self, cmd)

    def OnToolbarCompile(self, event):
        if self.editing:
            if utils.SaveEbuild(self):
                cmd = 'FEATURES="%s" USE="%s" /usr/sbin/ebuild %s compile' % \
                    (self.pref['features'], self.pref['use'], self.filename)
                utils.ExecuteInLog(self, cmd)

    def OnToolbarInstall(self, event):
        if self.editing:
            if utils.SaveEbuild(self):
                cmd = 'FEATURES="%s" USE="%s" /usr/sbin/ebuild %s install' % \
                    (self.pref['features'], self.pref['use'], self.filename)
                utils.ExecuteInLog(self, cmd)

    def OnToolbarQmerge(self, event):
        """ run /usr/sbin/ebuild (this ebuild) qmerge"""
        if self.editing:
            if utils.SaveEbuild(self):
                cmd = 'FEATURES="%s" USE="%s" /usr/sbin/ebuild %s qmerge' % \
                    (self.pref['features'], self.pref['use'], self.filename)
                utils.write(self, cmd)
                utils.ExecuteInLog(self, cmd)

    def OnMnuRepomanScan(self, event):
        """/usr/bin/repoman scan"""
        if self.editing:
            if '@gentoo.org' in  self.pref['email']:
                cvs = CVS(self)
                cvs.RepomanScan("scan")
            else:
                #utils.NotGentooDev()
                cvs.RepomanScan("--pretend scan")

    def OnMnuFullCommit(self, event):
        if self.editing:
            msg = \
            """This will do the following:
                1)  repoman --pretend full in PORTDIR_OVERLAY

                2)  Verify that ebuild has been emerged from PORTDIR_OVERLAY or 
                    inform you if its not installed -> "Are you sure?"

                3)  If new package:
                      add directory

                4) If not new package:
                     cvs update (package directory)
                     show output in log window, if anything wrong such as ebuild
                     existing, abort

                5)  Copy ebuild from PORTDIR_OVERLAY to CVS_DIR

                6)  cvs add ebuild

                7)  Prompt user to copy any files from FILES_DIR to CVS_DIR/FILES

                8)  cvs add anything new in CVS_DIR/FILES

                9)  Create digest for ebuild (should auto-add to cvs)

                10) echangelog dialog

                11) Show dialog with metadata.xml in case they need to change it
                    or create it

                12) If new package:
                      cvs add metadta.xml
                      cvs add ChangeLog

                13) Get commit message (could be same as echangelog msg)

                14) repoman full in CVS_DIR

                15) repoman --pretend commit -m "commit message"

                16) show diaglog (y/N): repoman commit -m "commit message"
                """
            #if (utils.MyMessage(self, msg, "Commit to CVS?", "info", cancel=1)):
            #    cvs = abeniCVS.CVS(self)
            #    cvs.FullCommit()
            #else:
            #    utils.write(self, "CVS commit Cancelled.")

            cvs = abeniCVS.CVS(self)
            cvs.FullCommit()
            self.log.ShowPosition(self.log.GetLastPosition())
            #self.log.ScrollToLine(self.log.GetEndAtLastLine() - 10)

    def OnMnuCVSupdate(self, event):
        """/usr/bin/cvs update"""
        if self.editing:
            cvs = CVS(self)
            cvs.CVSupdate()

    def OnMnuCopyFile(self, event):
        """Copy ebuild to cvs dir"""
        #TODO: Prompt if ebuild changes or if over-writing
        if self.editing:
            cvs = CVS(self)
            cvs.CopyEbuild()

    def OnMnuCopyMetadata(self, event):
        """Copy metadata.xml to cvs dir"""
        #TODO: Prompt if ebuild changes or if over-writing
        if self.editing:
            cvs = CVS(self)
            cvs.CopyMetadata()

    def OnMnuCreateCVSDigest(self, event):
        """Create digest in CVS dir"""
        if self.editing:
            cvs = CVS(self)
            cvs.CreateDigest()

    def OnMnuCVSaddDir(self, event):
        if self.editing:
            cvs = CVS(self)
            cvs.AddDir()

    def OnMnuCVSaddEbuild(self, event):
        if self.editing:
            cvs = CVS(self)
            cvs.AddEbuild()

    def OnMnuCVSaddDigest(self, event):
        if self.editing:
            cvs = CVS(self)
            cvs.AddDigest()

    def OnMnuCVSaddChangeLog(self, event):
        if self.editing:
            cvs = CVS(self)
            cvs.AddChangelog()

    def OnMnuCVSaddMetadata(self, event):
        if self.editing:
            cvs = CVS(self)
            cvs.AddMetadata()

    def OnMnuMetadataEdit(self, event):
        if self.editing:
            dlg = dialogs.MetadataDialog(self)
            dlg.CenterOnScreen()
            v = dlg.ShowModal()
            if v == wxID_OK:
                t = dlg.styledTextCtrl1.GetText()
                f = open(("%s/metadata.xml" % \
                  os.path.dirname(self.filename)), "w")
                f.write(t)
                f.close()
                dlg.Destroy()

    def OnMnuViewEnvironment(self, event):
        """Show environment file in editor window"""
        if not self.editing:
            return
        utils.ViewEnvironment(self)

    def OnMnuEchangelog(self, event):
        """Run echangelog for official Gentoo devs"""
        if not self.editing:
            return
        win = dialogs.EchangelogDialog(self, -1, "echangelog entry", \
                                       size=wxSize(350, 200), \
                                       style = wxDEFAULT_DIALOG_STYLE \
                                       )
        win.CenterOnScreen()
        val = win.ShowModal()
        if val == wxID_OK:
            os.chdir(os.path.dirname(self.filename))
            l = win.inp.GetValue()
            if l:
                utils.ExecuteInLog(self, "/usr/bin/echangelog %s" % l)
            else:
                #Not all xterms (konsole, eterm etc) have -hold feature, so 
                #we use actual xterm
                #("%s -hold -e /usr/bin/echangelog" % self.pref['xterm'])
                os.system("xterm -hold -e /usr/bin/echangelog")
        win.Destroy()

    def OnMnuGetTemplate(self, event):
        """"""
        if not self.editing:
            return

        c = utils.GetTemplates(self)
        c.sort()
        dlg = wxSingleChoiceDialog(self, 'Templates:', 'Choose template:',
                                   c, wxOK|wxCANCEL)
        if dlg.ShowModal() == wxID_OK:
            opt = dlg.GetStringSelection().strip()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        #Not quite sure how I feel about this:
        func = "my%s" % opt
        exec "from Templates import " + func
        cmd = "%s(self)" % func
        exec cmd


    def OnMnuViewConfigure(self, event):
        """Show configure file in editor window"""
        if not self.editing:
            return
        if not utils.CheckUnpacked(self):
            msg = 'You need to unpack first'
            title = 'Error'
            utils.MyMessage(self, msg, title, "error")
            return
        s = utils.GetS(self)
        if s:
            if os.path.exists('%s/configure' % s):
                utils.ViewConfigure(self)
            else:
                msg = 'No "configure" found in %s' % s
                title = 'Error'
                utils.MyMessage(self, msg, title, "error")

    def OnMnuViewMakefile(self, event):
        """Show Makefile in editor window"""
        if not self.editing:
            return
        s = utils.GetS(self)
        if s:
            if os.path.exists('%s/Makefile' % s):
                utils.ViewMakefile(self)
            else:
                msg = 'No Makefile found in %s' % s
                title = 'Error'
                utils.MyMessage(self, msg, title, "error")
        else:
                msg = 'You need to unpack the package first'
                title = 'Error'
                utils.MyMessage(self, msg, title, "error")

    def OnMnuLoadFromOverlay(self, event):
        """Load an ebuild from list of overlay ebuilds only"""
        if not utils.VerifySaved(self):
            cmd = "find %s -name '*.ebuild'" % portdir_overlay
            r, choices = utils.RunExtProgram(cmd)
            choices.sort()
            out = []
            for l in choices:
                out.append(l.replace(('%s/' % portdir_overlay), ''))
            dlg = wxSingleChoiceDialog(self, 'Load overlay ebuild:', \
                                      'Load overlay ebuild', out, wxOK|wxCANCEL)
            if dlg.ShowModal() == wxID_OK:
                e = dlg.GetStringSelection()
                if self.editing:
                    utils.ClearNotebook(self)
                filename = "%s/%s" % (portdir_overlay, e)
                utils.LoadEbuild(self, filename, portdir)
                self.filehistory.AddFileToHistory(filename)
            dlg.Destroy()

    def OnMnuEclassHelp(self, event):
        """View an eclass file"""
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

    def OnMnuDevPref(self, event):
        """Modify developer preferences"""
        win = dialogs.DevPrefs(self)
        win.CenterOnScreen()
        val = win.ShowModal()
        if val == wxID_OK:
            self.pref['userName'] = win.userName.GetValue()
            self.pref['cvsOptions'] = win.cvsOptions.GetValue()
            self.pref['cvsRoot'] = win.cvsRoot.GetValue()
            f = open(os.path.expanduser('~/.abeni/abenirc'), 'w')
            for v in self.pref.keys():
                f.write('%s = %s\n' % (v, self.pref[v]))
            f.close()

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
            self.pref['email'] = win.email.GetValue()
            self.pref['statuslist'] = win.statuslist.GetValue()
            f = open(os.path.expanduser('~/.abeni/abenirc'), 'w')

            for v in self.pref.keys():
                f.write('%s = %s\n' % (v, self.pref[v]))
            f.close()

    def OnMnuAbout(self, event):
        """Obligitory About me and my app screen"""
        #msg = 'Abeni %s  is a Python and wxPython application\n' \
        #      'by Rob Cakebread released under the GPL license.\n\n' \
        #      'Contributors: Marius Mauch' % __version__
        #title = 'About Abeni %s ' % __version__
        #utils.MyMessage(self, msg, title)
        about = dialogs.MyAboutBox(self)
        about.ShowModal()
        about.Destroy()

    def OnMnuExport(self, event):
        """Export ebuild and auxiliary files as tarball"""
        if not self.editing:
            return
        utils.ExportEbuild(self)

    def OnMnuBugzilla(self, event):
        """Dialog to add bugzilla info"""
        if not self.editing:
            return
        dlg = dialogs.BugzillaDialog(self)
        dlg.CenterOnScreen()
        v = dlg.ShowModal()
        if v == wxID_OK:
            r = dlg.SaveInfo()
            dlg.Destroy()

    def OnMnuNewFunction(self, event):
        """Dialog to add new function"""
        if not self.editing:
            return
        dlg = dialogs.NewFunction(self)
        dlg.CenterOnScreen()
        v = dlg.ShowModal()
        if v == wxID_OK:
            func, val = dlg.GetFunc()
            utils.AddFunc(self, func, val)
        self.saved = 0
        dlg.Destroy()

    def OnMnuClearLog(self, event):
        """Clear the log window"""
        self.log.SetValue('')

    def KillProc(self, event):
        """Kill processes when stop button clicked"""
        os.system("kill %s" % self.pid)
        utils.write(self, "Killed %s" % self.pid)
        try:
            pid = open("/tmp/abeni_proc.pid", "r").read().strip()
            os.system("kill %s" % pid)
            utils.write(self, "sub pid %s killed" % pid)
        except:
            pass

    def OnPageChanging(self, event):
        """Catch event when page in notebook is going to change"""
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
        event.Skip()

    def OnProcessEnded(self, evt):
        #utils.write('OnProcessEnded, pid:%s,  exitCode: %s\n' %
        #               (evt.GetPid(), evt.GetExitCode()))
        stream = self.process.GetInputStream()
        if stream.CanRead():
            text = stream.read()
            text = string.split(text, '\n')
            for t in text:
                utils.write(self, t)
        self.process.Destroy()
        self.process = None
        self.tb.EnableTool(self.toolStopID, False)
        self.running = None
        action = self.action
        self.action = None
        utils.PostAction(self, action)
        self.timer.Stop()
        #self.log.SetInsertionPointEnd()
        self.log.ShowPosition(self.log.GetLastPosition())

    def OnToolbarXterm(self, event):
        """Launch xterm in ${S}"""
        if not self.editing:
            return
        if not utils.CheckUnpacked(self):
            msg = 'You need to unpack the package first.'
            title = 'Error'
            utils.MyMessage(self, msg, title, "error")
        else:
            c = os.getcwd()
            p = utils.GetP(self)
            mys = utils.GetS(self)
            if os.path.exists(self.s):
                os.chdir(self.s)
            elif os.path.exists(mys):
                os.chdir(mys)
            else:
                try:
                    os.chdir('%s/portage/%s/work/' % (portage_tmpdir, p))
                except:
                    pass
            if self.pref['xterm']:
                try:
                    os.system('%s &' % self.pref['xterm'])
                    os.chdir(c)
                except:
                    pass
            else:
                utils.MyMessage(self, "Set xterm in preferences", \
                  "Error - no xterm", "error")

    def OnMnuEdit(self, event=None, save=1, filename=''):
        """Launch external editor then reload ebuild after editor exits"""
        if self.editing:
            if not self.pref['editor']:
                utils.MyMessage(self, "No editor defined in perferences", \
                  "Error: no editor defined", "error")
            if save:
                utils.SaveEbuild(self)
            utils.ClearNotebook(self)
            wxSafeYield()
            if not filename:
                f = self.filename
            else:
                f = filename
            os.system('%s %s' % (self.pref['editor'], f))
            utils.LoadEbuild(self, f, portdir)

    def OnMnuRepoman(self, event):
        """Run repoman --pretend full on this ebuild"""
        if not self.editing:
            return
        cmd = 'cd %s;/usr/bin/repoman --pretend full' % self.ebuildDir
        utils.ExecuteInLog(self, cmd)

    def OnMnuEmerge(self, event):
        """Run 'emerge <options> <this ebuild>' """
        #TODO: Don't emerge filename explicitly
        if not self.editing:
            return
        if utils.SaveEbuild(self):
            win = dialogs.EmergeDialog(self, -1, "Enter emerge options", \
                                size=wxSize(350, 350), \
                                style = wxDEFAULT_DIALOG_STYLE \
                                )
            win.CenterOnScreen()
            val = win.ShowModal()
            emergeCmd = win.emerge.GetValue()
            use = win.use.GetValue()
            features = win.features.GetValue()
            if emergeCmd[:8] != 'ACCEPT_K':
                utils.write(self, "Cancelled: %s " % emergeCmd)
                return
            if val == wxID_OK:
                cmd = 'USE="%s" FEATURES="%s" %s' % (use, features, emergeCmd)
                utils.write(self, cmd)
                utils.ExecuteInLog(self, cmd)

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

        if utils.SaveEbuild(self):
            cmd = 'USE="%s" FEATURES="%s" /usr/sbin/ebuild %s %s' % \
              (self.pref['use'], self.pref['features'], self.filename, opt)
            utils.write(self, 'Executing:\n%s' % cmd)
            utils.ExecuteInLog(self, cmd)

    def OnMnuDelVariable(self, event):
        """Delete custom variable"""
        if not self.editing:
            return
        self.saved = 0
        utils.DelVariable(self)

    def OnMnuExploreD(self, event):
        """Launch file manager in ${D}"""
        if not self.editing:
            return

        p = utils.GetP(self)
        D = '%s/portage/%s/image' % (portage_tmpdir, p)
        if not os.path.exists(D):
            utils.MyMessage(self, "${D} hasn't been created. Run src_install()", \
              "Error", "error")
            return
        else:
            os.chdir(D)
            if self.pref['fileBrowser']:
                os.system('%s %s &' % (self.pref['fileBrowser'], D))
            else:
                utils.MyMessage(self, "Set file manager in preferences", "Error", \
                  "error")

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
            utils.AddNewVar(self, newVariable, "")
        self.saved = 0
        dlg.Destroy()

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
        mnuLoadOverlayID=wxNewId()
        menu_file.Append(mnuLoadOverlayID, "Load ebuild from &overlay dir")
        EVT_MENU(self, mnuLoadOverlayID, self.OnMnuLoadFromOverlay)
        mnuSaveID=wxNewId()
        menu_file.Append(mnuSaveID, "&Save ebuild")
        EVT_MENU(self, mnuSaveID, self.OnMnuSave)
        mnuExportID=wxNewId()
        menu_file.Append(mnuExportID, "&Export ebuild")
        EVT_MENU(self, mnuExportID, self.OnMnuExport)
        mnuExitID=wxNewId()
        menu_file.Append(mnuExitID, "E&xit\tAlt-X")
        EVT_MENU(self, mnuExitID, self.OnMnuExit)
        menubar = wxMenuBar()
        menubar.Append(menu_file, "&File")

        self.filehistory = wxFileHistory(9)
        self.filehistory.UseMenu(self.menu)
        # Variable
        menu_variable = wxMenu()
        mnuNewVariableID = wxNewId()
        menu_variable.Append(mnuNewVariableID, "&New Variable\tF2", \
          "New Variable")
        EVT_MENU(self, mnuNewVariableID, self.OnMnuNewVariable)
        mnuDelVariableID = wxNewId()
        menu_variable.Append(mnuDelVariableID, "&Delete Variable")
        EVT_MENU(self, mnuDelVariableID, self.OnMnuDelVariable)
        menubar.Append(menu_variable, "&Variable")
        # Function
        menu_function = wxMenu()
        mnuNewFunctionID = wxNewId()
        menu_function.Append(mnuNewFunctionID, "&New Function\tF3", \
          "New Function")
        EVT_MENU(self, mnuNewFunctionID, self.OnMnuNewFunction)
        mnuDelFunctionID = wxNewId()
        menu_function.Append(mnuDelFunctionID, "&Delete Function")
        EVT_MENU(self, mnuDelFunctionID, self.OnMnuDelFunction)
        menubar.Append(menu_function, "Functio&n")
        # Eclass
        menu_eclass = wxMenu()
        mnuGetTemplateID = wxNewId()
        menu_eclass.Append(mnuGetTemplateID, "&Load template")
        EVT_MENU(self, mnuGetTemplateID, self.OnMnuGetTemplate)
        menubar.Append(menu_eclass, "Temp&lates")

        # Tools
        menu_tools = wxMenu()
        mnuEbuildID = wxNewId()
        menu_tools.Append(mnuEbuildID, \
          "Run &ebuild <this ebuild> <command>\tf4")
        EVT_MENU(self, mnuEbuildID, self.OnMnuEbuild)
        mnuEmergeID = wxNewId()
        menu_tools.Append(mnuEmergeID, "Run e&merge <args> <this ebuild>\tf5")
        EVT_MENU(self, mnuEmergeID, self.OnMnuEmerge)
        #mnuLintoolID = wxNewId()
        mnuGetDepsID = wxNewId()
        menu_tools.Append(mnuGetDepsID, "Fix la&zy R/DEPEND")
        EVT_MENU(self, mnuGetDepsID, self.OnMnuGetDeps)
        mnuEchangelogID = wxNewId()
        #menu_tools.Append(mnuLintoolID, "Run &Lintool on this ebuild")
        #EVT_MENU(self, mnuLintoolID, self.OnMnuLintool)
        mnuRepomanID = wxNewId()
        menu_tools.Append(mnuRepomanID, "Run &repoman --pretend full")
        EVT_MENU(self, mnuRepomanID, self.OnMnuRepoman)
        mnuDigestID = wxNewId()
        menu_tools.Append(mnuDigestID, "&Create Digest in PORTDIR_OVERLAY")
        EVT_MENU(self, mnuDigestID, self.OnMnuCreateDigest)
        mnuClearLogID = wxNewId()
        menu_tools.Append(mnuClearLogID, "Clear log &window\tF11")
        EVT_MENU(self, mnuClearLogID, self.OnMnuClearLog)
        menubar.Append(menu_tools, "&Tools")

        # Project
        menu_proj = wxMenu()
        mnuBugID = wxNewId()
        menu_proj.Append(mnuBugID, "Bug&zilla info")
        EVT_MENU(self, mnuBugID, self.OnMnuBugzilla)
        mnuSumID = wxNewId()
        menu_proj.Append(mnuSumID, "&Project Manager")
        EVT_MENU(self, mnuSumID, self.OnMnuProjManager)
        menubar.Append(menu_proj, "&Project")

        #CVS
        menu_cvs = wxMenu()
        submenu_cvs = wxMenu()

        #menuXtermID = wxNewId()
        #menu_tools.Append(mnuXtermID, "x&term in CVS dir")
        #EVT_MENU(self, mnuXtermID, self.OnMnuXtermCVS)

        #TODO: Only add CVS menu if dev preferences is filled in
        mnuFullCommitID = wxNewId()
        menu_cvs.Append(mnuFullCommitID, "&commit ebuild to CVS (Use this)")
        EVT_MENU(self, mnuFullCommitID, self.OnMnuFullCommit)

        mnuMetadataEditID = wxNewId()
        submenu_cvs.Append(mnuMetadataEditID, "edit/create metadata")
        EVT_MENU(self, mnuMetadataEditID, self.OnMnuMetadataEdit)

        mnuRepomanScanID = wxNewId()
        submenu_cvs.Append(mnuRepomanScanID, "&repoman scan")
        EVT_MENU(self, mnuRepomanScanID, self.OnMnuRepomanScan)

        mnuCVSupdateID = wxNewId()
        submenu_cvs.Append(mnuCVSupdateID, "cvs u&pdate")
        EVT_MENU(self, mnuCVSupdateID, self.OnMnuCVSupdate)

        mnuCopyEbuildID = wxNewId()
        submenu_cvs.Append(mnuCopyEbuildID, "Cop&y ebuild to CVS dir")
        EVT_MENU(self, mnuCopyEbuildID, self.OnMnuCopyFile)

        mnuDigestID = wxNewId()
        submenu_cvs.Append(mnuDigestID, "&Create Digest in CVS dir")
        EVT_MENU(self, mnuDigestID, self.OnMnuCreateCVSDigest)

        mnuCVSaddID = wxNewId()
        submenu_cvs.Append(mnuCVSaddID, "&cvs add ebuild")
        EVT_MENU(self, mnuCVSaddID, self.OnMnuCVSaddEbuild)

        mnuCVSaddMetadataID = wxNewId()
        submenu_cvs.Append(mnuCVSaddMetadataID, "&cvs add metadata.xml")
        EVT_MENU(self, mnuCVSaddMetadataID, self.OnMnuCVSaddMetadata)

        mnuCVSaddDigestID = wxNewId()
        submenu_cvs.Append(mnuCVSaddDigestID, "&cvs add digest")
        EVT_MENU(self, mnuCVSaddDigestID, self.OnMnuCVSaddDigest)

        mnuCVSaddDirID = wxNewId()
        submenu_cvs.Append(mnuCVSaddDirID, "&cvs add directory")
        EVT_MENU(self, mnuCVSaddDirID, self.OnMnuCVSaddDir)

        #~ mnuClearLogID = wxNewId()
        #~ submenu_cvs.Append(mnuEchangelogID, "Run ec&hangelog for this ebuild")
        #~ EVT_MENU(self, mnuEchangelogID, self.OnMnuEchangelog)

        #~ mnuGetDepsID = wxNewId()
        #~ submenu_cvs.Append(mnuEchangelogID,"Edit ChangeLog in external editor")
        #~ EVT_MENU(self, mnuEchangelogID, self.OnMnuEditChangeLog)

        #~ mnuRepoCommitID = wxNewId()
        #~ submenu_cvs.Append(mnuRepoScanID, "repoman com&mit")
        #~ EVT_MENU(self, mnuRepoCommitID, self.OnMnuRepoCommit)
        submenu_cvsID=wxNewId()
        menu_cvs.AppendMenu(submenu_cvsID, "&manual CVS operations", submenu_cvs)
        menubar.Append(menu_cvs, "&CVS")

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
        mnuEditID = wxNewId()
        menu_view.Append(mnuEditID, "This ebuild in e&xternal editor\tf7")
        EVT_MENU(self, mnuEditID, self.OnMnuEdit)
        mnuExploreDid = wxNewId()
        menu_view.Append(mnuExploreDid, "File browser in ${D}")
        EVT_MENU(self, mnuExploreDid, self.OnMnuExploreD)
        menubar.Append(menu_view, "Vie&w")
        # Options
        self.menu_options = wxMenu()
        mnuPrefID = wxNewId()
        self.menu_options.Append(mnuPrefID, "&Global Preferences")
        EVT_MENU(self, mnuPrefID, self.OnMnuPref)
        mnuDevPrefID = wxNewId()
        self.menu_options.Append(mnuDevPrefID, "&Developer Preferences")
        EVT_MENU(self, mnuDevPrefID, self.OnMnuDevPref)
        self.menu_options.AppendSeparator()
        self.mnuLogBottomID = wxNewId()
        self.menu_options.Append(self.mnuLogBottomID, "Log at &bottom\tf9", \
          "", wxITEM_RADIO)
        EVT_MENU(self, self.mnuLogBottomID, self.OnMnuLogBottom)
        self.mnuLogWindowID = wxNewId()
        self.menu_options.Append(self.mnuLogWindowID, \
          "Log in separate &window\tf10", "", wxITEM_RADIO)
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

