#!/usr/bin/env python

"""Abeni - Gentoo Linux Ebuild Editor/Syntax Checker
Released under the terms of the GNU Public License v2"""

__author__ = 'Rob Cakebread'
__email__ = 'robc@myrealbox.com'
__version__ = '0.0.5'
__changelog_ = 'http://abeni.sf.net/ChangeLog'

print "Importging portage config, wxPython, Python and Abeni modules..."
from portage import config
from wxPython.wx import *
from wxPython.lib.dialogs import wxScrolledMessageDialog
import os, string, sys, re, urlparse
import dialogs, panels, options

#Get portage path locations from /etc/make.conf
distdir = config().environ()['DISTDIR']
portdir = config().environ()['PORTDIR']
portdir_overlay = config().environ()['PORTDIR_OVERLAY']

defaults = ["SRC_URI", "HOMEPAGE", "DEPEND", "RDEPEND", "DESCRIPTION", "S", "IUSE", "SLOT", "KEYWORDS", "LICENSE"]

class MyFrame(wxFrame):

    """ Main frame that holds the menu, toolbar and notebook """

    def __init__(self, parent, id, title):
        wxFrame.__init__(self, parent, -1, title, size=wxSize(800,500))
        self.SetAutoLayout(true)
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
        self.GetOptions()
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
        #application icon 16x16
        iconFile = ('/usr/share/pixmaps/abeni/abeni_logo16.png')
        icon = wxIcon(iconFile, wxBITMAP_TYPE_PNG)
        self.SetIcon(icon)
        #Setup wxNotebook in main frame
        self.nb = wxNotebook(self, -1)
        lc = wxLayoutConstraints()
        lc.top.SameAs(self, wxTop, 0)
        lc.left.SameAs(self, wxLeft, 0)
        lc.bottom.SameAs(self, wxBottom, 0)
        lc.right.SameAs(self, wxRight, 0)
        self.nb.SetConstraints(lc)
        self.sb = self.CreateStatusBar(1, wxST_SIZEGRIP)
        self.sb.SetFieldsCount(2)
        EVT_NOTEBOOK_PAGE_CHANGED(self.nb, self.nb.GetId(), self.OnPageChanged)
        #Create menus, setup keyboard accelerators
        # File
        self.menu = menu_file = wxMenu()
        mnuNewID=wxNewId()
        menu_file.Append(mnuNewID, "&New ebuild")
        mnuLoadID=wxNewId()
        menu_file.Append(mnuLoadID, "&Load ebuild")
        EVT_MENU(self, mnuLoadID, self.OnMnuLoad)
        mnuSaveID=wxNewId()
        menu_file.Append(mnuSaveID, "&Save ebuild")
        EVT_MENU(self, mnuSaveID, self.OnMnuSave)
        mnuExitID=wxNewId()
        menu_file.Append(mnuExitID, "E&xit  (Alt-x)")
        EVT_MENU(self, mnuExitID, self.OnMnuExit)
        menubar = wxMenuBar()
        menubar.Append(menu_file, "&File")
        EVT_MENU(self, mnuNewID, self.OnMnuNew)
        EVT_MENU_RANGE(self, wxID_FILE1, wxID_FILE9, self.OnFileHistory)
        self.filehistory = wxFileHistory()
        self.filehistory.UseMenu(self.menu)
        EVT_WINDOW_DESTROY(self, self.Cleanup)
        # Edit
        menu_edit = wxMenu()
        mnuNewVariableID = wxNewId()
        menu_edit.Append(mnuNewVariableID, "New &Variable")
        EVT_MENU(self, mnuNewVariableID, self.OnMnuNewVariable)
        mnuNewFunctionID = wxNewId()
        menu_edit.Append(mnuNewFunctionID, "New &Function")
        EVT_MENU(self, mnuNewFunctionID, self.OnMnuNewFunction)
        mnuDelVariableID = wxNewId()
        menu_edit.Append(mnuDelVariableID, "De&lete Variable")
        EVT_MENU(self, mnuDelVariableID, self.OnMnuDelVariable)
        mnuDelFunctionID = wxNewId()
        menu_edit.Append(mnuDelFunctionID, "&Delete Function")
        EVT_MENU(self, mnuDelFunctionID, self.OnMnuDelFunction)
        menubar.Append(menu_edit, "&Edit")
        # Eclass
        menu_eclass = wxMenu()
        mnuDistutilsID = wxNewId()
        menu_eclass.Append(mnuDistutilsID, "distutils")
        EVT_MENU(self, mnuDistutilsID, self.OnMnuEclassDistutils)
        mnuCVSID = wxNewId()
        menu_eclass.Append(mnuCVSID, "cvs")
        EVT_MENU(self, mnuCVSID, self.OnMnuEclassCVS)
        menubar.Append(menu_eclass, "E&class")
        # Tools
        menu_tools = wxMenu()
        mnuEbuildID = wxNewId()
        menu_tools.Append(mnuEbuildID, "Run &ebuild <this ebuild> <command>")
        EVT_MENU(self, mnuEbuildID, self.OnMnuEbuild)
        mnuEmergeID = wxNewId()
        menu_tools.Append(mnuEmergeID, "Run e&merge <args> <this ebuild>")
        EVT_MENU(self, mnuEmergeID, self.OnMnuEmerge)
        mnuLintoolID = wxNewId()
        menu_tools.Append(mnuLintoolID, "Run &Lintool on this ebuild")
        EVT_MENU(self, mnuLintoolID, self.OnMnuLintool)
        mnuRepomanID = wxNewId()
        menu_tools.Append(mnuRepomanID, "Run &Repoman on this ebuild")
        EVT_MENU(self, mnuRepomanID, self.OnMnuRepoman)
        mnuDigestID = wxNewId()
        menu_tools.Append(mnuDigestID, "&Create Digest")
        EVT_MENU(self, mnuDigestID, self.OnMnuCreateDigest)
        mnuDiffID = wxNewId()
        menu_tools.Append(mnuDiffID, "Observe &diff")
        EVT_MENU(self, mnuDiffID, self.OnMnuDiff)
        mnuDiffCreateID = wxNewId()
        menu_tools.Append(mnuDiffCreateID, "Create diff &file")
        EVT_MENU(self, mnuDiffCreateID, self.OnMnuDiffCreate)

        menubar.Append(menu_tools, "&Tools")
        # Options
        menu_options = wxMenu()
        mnuPrefID = wxNewId()
        menu_options.Append(mnuPrefID, "&Global Preferences")
        menubar.Append(menu_options, "&Options")
        EVT_MENU(self, mnuPrefID, self.OnMnuPref)
        # Help
        menu_help = wxMenu()
        mnuHelpID = wxNewId()
        mnuHelpRefID = wxNewId()
        mnuAboutID = wxNewId()
        menu_help.Append(mnuHelpID,"&Contents")
        EVT_MENU(self, mnuHelpID, self.OnMnuHelp)
        menu_help.Append(mnuHelpRefID,"&Ebuild Quick Reference")
        EVT_MENU(self, mnuHelpRefID, self.OnMnuHelpRef)
        menu_help.Append(mnuAboutID,"&About")
        EVT_MENU(self, mnuAboutID, self.OnMnuAbout)
        menubar.Append(menu_help,"&Help")
        self.SetMenuBar(menubar)
        # Keyboard accelerators
        # Alt-x to exit
        #BUG: This doesn't work when you first open Abeni. You have to be editting an ebuild:
        aTable = wxAcceleratorTable([(wxACCEL_ALT,  ord('x'), mnuExitID)])
        self.SetAcceleratorTable(aTable)
        #Create Toolbar with icons

        self.tb = self.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT) #wxTB_3DBUTTONS
        #self.tb.SetToolSeparation(10)
        newID = wxNewId()
        newBmp = ('/usr/share/pixmaps/abeni/new.png')
        self.tb.AddSimpleTool(newID, wxBitmap(newBmp, wxBITMAP_TYPE_PNG), \
                                "Create new ebuild", "Create New ebuild")
        EVT_TOOL(self, newID, self.OnMnuNew)

        openID = wxNewId()
        openBmp = ('/usr/share/pixmaps/abeni/open.png')
        self.tb.AddSimpleTool(openID, wxBitmap(openBmp, wxBITMAP_TYPE_PNG), \
                                "Open ebuild", "Open ebuild")
        EVT_TOOL(self, openID, self.OnMnuLoad)
        saveID = wxNewId()
        saveBmp = ('/usr/share/pixmaps/abeni/save.png')
        self.tb.AddSimpleTool(saveID, wxBitmap(saveBmp, wxBITMAP_TYPE_PNG), \
                                "Save ebuild", "Save ebuild")
        EVT_TOOL(self, saveID, self.OnMnuSave)
        self.tb.AddSeparator()
        self.tb.AddSeparator()
        newVarID = wxNewId()
        newVarBmp = ('/usr/share/pixmaps/abeni/x.png')
        self.tb.AddSimpleTool(newVarID, wxBitmap(newVarBmp, wxBITMAP_TYPE_PNG), \
                                "New Variable", "New Variable")
        EVT_TOOL(self, newVarID, self.OnMnuNewVariable)
        newFunID = wxNewId()
        newFunBmp = ('/usr/share/pixmaps/abeni/fx.png')
        self.tb.AddSimpleTool(newFunID, wxBitmap(newFunBmp, wxBITMAP_TYPE_PNG), \
                                "New Function", "New Function")
        EVT_TOOL(self, newFunID, self.OnMnuNewFunction)
        self.tb.AddSeparator()
        lintoolID = wxNewId()
        lintoolBmp = ('/usr/share/pixmaps/abeni/lintool.png')
        self.tb.AddSimpleTool(lintoolID, wxBitmap(lintoolBmp, wxBITMAP_TYPE_PNG), \
                                "Lintool - check syntax of ebuild", "Run Lintool on this ebuild")
        EVT_TOOL(self, lintoolID, self.OnMnuLintool)
        toolDigestID = wxNewId()
        digestBmp = ('/usr/share/pixmaps/abeni/digest.png')
        self.tb.AddSimpleTool(toolDigestID, wxBitmap(digestBmp, wxBITMAP_TYPE_PNG), \
                                "Create digest for this ebuild", "Create digest for this ebuild")
        EVT_TOOL(self, toolDigestID, self.OnMnuCreateDigest)
        self.tb.AddSeparator()
        helpID = wxNewId()
        helpBmp = ('/usr/share/pixmaps/abeni/help.png')
        self.tb.AddSimpleTool(helpID, wxBitmap(helpBmp, wxBITMAP_TYPE_PNG), \
                                "Help", "Abeni Help")
        EVT_TOOL(self, helpID, self.OnMnuHelp)
        #Load recent ebuilds to File menu
        for ebuild in self.recentList:
            self.filehistory.AddFileToHistory(ebuild.strip())

        self.tb.Realize()
        EVT_TOOL_ENTER(self, -1, self.OnToolZone)
        EVT_TIMER(self, -1, self.OnClearSB)
        self.timer = None

        #Load ebuild if specified on command line, by filename or by full package name
        if len(sys.argv) == 2:
            f = sys.argv[1]
            if os.path.exists(f):
                self.LoadEbuild(f)
            else:
                print "No such file: " + f
                print "Checking for package: " + f
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
                        cat = string.split(s[:-4], '/')[0]
                        package = string.split(s[:-4], '/')[1]
                        if s[-7:] == 'OVERLAY':
                            fname = portdir_overlay + '/' + cat + '/' + f + '/' + package + '.ebuild'
                        else:
                            fname = portdir + '/' + cat + '/' + f + '/' + package + '.ebuild'
                        self.LoadEbuild(fname)
                    dlg.Destroy()
                else:
                    print "Package " + f + " not found. Be sure to use full package name."


    def Cleanup(self, *args):
        """Cleanup for filehistory"""
        # No idea why this is used. It was in the demo code. It breaks in wxPython 2.4.2.1
        # because object doesn't exist after notebook is removed then added.
        del self.filehistory


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
        varList = self.panelMain.GetVars()
        l = []
        for key in varList:
            l.append(key.GetLabel())
        dlg = wxSingleChoiceDialog(self, 'Choose variable to DELETE:', 'Delete Variable',
                            l, wxOK|wxCANCEL)
        if dlg.ShowModal() == wxID_OK:
            f = dlg.GetStringSelection()
            #print f
            for key in varList:
                if key.GetLabel() == f:
                    varList[key].Destroy()
                    key.Destroy()
                    del varList[key]
                    break
        dlg.Destroy()

    def AddCommand(self, command):
        t = self.panelMain.stext.GetValue()
        t += (command + "\n")
        self.panelMain.stext.SetValue(t)

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
        cmd = 'diff -u ' + self.lastFile + ' ' + self.filename + ' > ~/.abeni/' + diffFile
        #print cmd
        os.system(cmd)

    def OnMnuCreateDigest(self, event):
        """Run 'ebuild filename digest' on this ebuild"""
        if not self.editing:
            return

        # I did this in an xterm because we need to be root and it has colored output.
        #TODO: Strip escape codes so we can put in a text widget for those who use sudo

        cmd = 'su -c "ebuild ' + self.filename + ' digest"'
        os.system(self.pref['xterm'] + ' -T "Creating Digest" -hold -e ' + cmd + ' &')

    def OnMnuRepoman(self, event):
        """Run 'repoman-local-5.py' on this ebuild"""
        if not self.editing:
            return
        d = os.getcwd()
        os.chdir(self.ebuildDir)
        cmd = '"/usr/bin/repoman-safe.py ; echo Press ENTER ; read foo"'
        cmd2 = self.pref['xterm'] + ' -T "repoman-safe" -e ' + cmd + ' &'
        os.system(cmd2)
        os.chdir(d)


    def OnMnuEmerge(self, event):
        """Run 'emerge <options> <this ebuild>' """
        if not self.editing:
            return

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
            cmd = '"emerge ' + opts + ' ' + self.filename + ' ; echo Done"'
        else:
            if opts == 'unmerge' or opts == '-C':
                cmd = 'su -c "emerge ' + opts + ' ' + self.package + ' ; echo Done"'
            else:
                cmd = 'su -c "emerge ' + opts + ' ' + self.filename + ' ; echo Done"'
        cmd2 = self.pref['xterm'] + ' -T "emerge" -hold -e ' + cmd + ' &'
        os.system(cmd2)


    def OnMnuEbuild(self, event):
        """Run 'ebuild <file> <cmd>' """
        if not self.editing:
            return
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
        cmd = 'su -c "ebuild ' + self.filename + ' ' + opt + ' ; echo Done"'
        cmd2 = self.pref['xterm'] + ' -T "ebuild" -hold -e ' + cmd + ' &'
        os.system(cmd2)

    def OnMnuLintool(self, event):
        """Run 'lintool' on this ebuild"""
        if not self.editing:
            return

        cmd = '"/usr/bin/lintool ' + self.filename + ' ; echo Press ENTER ; read foo"'
        #print cmd
        cmd2 = self.pref['xterm'] + ' -T "Lintool" -e ' + cmd + ' &'
        #print cmd2
        os.system(cmd2)

        #TODO use the Python tempfile module
        # This works, but need fixed width fonts:
        #tmp = '/tmp/lintool.txt'
        #os.system('lintool ' + self.filename + ' > ' + tmp)
        #l = open(tmp, 'r').read()
        # self.AddEditor('Lintool', l)

        #Can show in a dialog, but it might be annoying:
        #dlg = wxScrolledMessageDialog(self, l, "Lintool Results:")
        #dlg.ShowModal()

    def OnMnuDelFunction(self, event):
        """Remove current function page"""
        #TODO: This removes any page, change to only move functions.
        this = self.nb.GetSelection()
        n = 0
        for f in self.funcList:
            if f == self.nb.GetPage(this):
                self.nb.RemovePage(self.nb.GetSelection())
                break
            n += 1
        del self.funcList[n]
        #Neither of these fix the bug where the tab still shows. If you resize the window, it deletes it.
        #self.nb.Refresh(true)
        #self.Refresh(true)

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

    def LoadEbuild(self, filename):
        filename = string.strip(filename)
        self.SetFilename(filename)
        self.recentList.append(filename)
        vars = {}
        funcs = {}
        statements = []
        defaultVars = ['DESCRIPTION', 'HOMEPAGE', 'SRC_URI', 'LICENSE', 'SLOT'
                        'KEYWORDS', 'IUSE', 'DEPEND', 'S']
        f = open(filename, 'r')
        # Read in header, then discard it. We always write clean header.
        # This may change for developer version in future.
        f.readline()
        f.readline()
        f.readline()

        #Indenting shoud be done with tabs, not spaces
        badSpaces = re.compile('^ +')
        #Comments should be indented to level of code its refering to.
        badComments = re.compile('^#+')
        while 1:
            l = f.readline()
            if not l: #End of file
                break
            if l !='\n':
                l = string.strip(l)

            # Variables always start a line with all caps and has an =
            varTest = re.search('^[A-Z]+.*= ?', l)

            # Match any of these:
            #  mine() {
            #  mine () {   # I hate when people use this one.
            #  my_func() {
            #  my_func () {
            #  Any above with { on separate line
            funcTest = re.search('^[a-zA-Z]*(_[a-zA-Z]*)?(_[a-zA-Z]*)? ?\(\)', l)

            if varTest:
                s = string.split(l, "=")
                if len(s) > 2:  # RDEPEND = ">=foolib2"   (has two equal signs)
                    s[1] = s[1] + "=" + s[2] + "\n"
                #Multi-line variables
                if l.count('"') == 1:
                    v = s[1] + '\n'
                    while 1:
                        l = f.readline()
                        v += l
                        if l.count('"') == 1:
                            #print s[0], v
                            s[1] = v.replace('\t', '')
                            s[1] = s[1].replace('\n\n', '\n')
                            break
                vars[s[0]] = s[1]
                self.varOrder.append(s[0])
                continue

            if funcTest:
                tempf = []
                fname = string.replace(l, "{", "")
                tempf.append(l + "\n")
                while 1:
                    l = f.readline()
                    #replace spaces with tabs
                    l = badSpaces.sub('\t', l)
                    l = badComments.sub('\t#', l)
                    tempf.append(l)
                    if l[0] == "}":
                        s = ""
                        for ls in tempf:
                            s += ls
                        funcs[fname] = s
                        self.funcOrder.append(fname)
                        break
                continue
            # Command like 'inherit cvs' or a comment
            if re.search('^([a-z]|#|\[)', l):
                self.statementList.append(l)

        f.close()
        '''
        print self.statementList
        t = string.join(self.statementList, '\n')
        print t
        dups = re.compile(r"""\n\n\n""", re.DOTALL)
        t = dups.sub('\n', t)
        print t
        self.statementList= string.split(t, '\n')
        print self.statementList
        '''
        s = string.split(filename, "/")
        self.ebuild_file = s[len(s)-1]
        package = s[len(s)-2]
        category = s[len(s)-3]
        defaultVars = {}
        otherVars = {}
        defaultVars, otherVars = self.SeparateVars(vars)
        defaultVars['package'] = package
        defaultVars['ebuild_file'] = self.ebuild_file
        defaultVars['category'] = category

        #If S isn't set it equals
        if defaultVars['S'] == '':
            defaultVars['S'] = '${WORKDIR}/${P}'

        #You must set IUSE, even if you don't use it.
        if defaultVars['IUSE'] == '':
            defaultVars['IUSE'] = '""'
        self.editing = 1
        self.AddPages()
        self.PopulateForms(defaultVars)
        clog = string.replace(filename, self.ebuild_file, '') + 'ChangeLog'
        self.ebuildDir = string.replace(filename, self.ebuild_file, '')
        self.panelChangelog.Populate(clog)
        #Add custom variables to Main panel

        #This was un-ordered:
        #for v in otherVars:
        #    self.AddNewVar(v, otherVars[v])

        # Put them in panel in the order they were in the ebuild
        for n in range(len(self.varOrder) -1):
            for v in otherVars:
                if v == self.varOrder[n]:
                    self.AddNewVar(v, otherVars[v])

        #Add functions in order they were in in ebuild:
        for n in range(len(self.funcOrder)):
            self.AddFunc(self.funcOrder[n], funcs[self.funcOrder[n]])
        self.panelMain.stext.SetValue(string.join(self.statementList, '\n'))

        # Add original ebuild file:
        self.AddEditor('Original File', open(filename, 'r').read())
        self.nb.SetSelection(0)

        # Set titlebar of app to ebuild name
        self.SetTitle(self.ebuild_file + ' | Abeni ' + __version__)

    def SeparateVars(self, vars):
        """Separates variables into defaults (defaultVars) and all others (vars)"""
        l = ["SRC_URI", "HOMEPAGE", "DEPEND", "RDEPEND", "DESCRIPTION", "S", "IUSE", "SLOT", "KEYWORDS", "LICENSE"]
        defaultVars = {}
        for key in l:
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
        if modified:
            dlg = wxMessageDialog(self, 'Save modified ebuild?\n' + self.filename,
                    'Save ebuild?', wxYES_NO | wxCANCEL | wxICON_INFORMATION)
            val = dlg.ShowModal()
            if val == wxID_YES:
                self.WriteEbuild()
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
            self.LoadEbuild(path)
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
                    self.LoadEbuild(filename)
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

    def GetOptions(self):
        """Global options from apprc file"""
        myOptions = options.Options()
        self.pref = myOptions.Prefs()

    def OnToolZone(self, event):
        """Clear statusbar 3 seconds after mouse moves over toolbar icon"""
        if self.timer is None:
            self.timer = wxTimer(self)
        if self.timer.IsRunning():
            self.timer.Stop()
        self.timer.Start(3000)
        event.Skip()

    def OnClearSB(self, event):
        """OnToolZone clear status bar after hovering over toolbar icon"""
        self.timer.Stop()
        self.timer = None

    def OnPageChanged(self, event):
        """Catch event when page in notebook is changed"""
        self.nbPage = event.GetSelection()
        event.Skip()

    def OnMnuEclassCVS(self, event):
        if not self.editing:
            return

        src_compile = "src_compile() {\n" + \
        "\texport WANT_AUTOCONF_2_5=1\n" + \
        "\tsh autogen.sh\n" + \
        "\teconf || die 'configure failed'\n" + \
        "\temake || die 'parallel make failed'\n" + \
        "}"

        src_install = "src_install() {\n" + \
        "\teinstall || die 'make install failed'\n" + \
        "}"

        self.AddNewVar("ECVS_SERVER", "")
        self.AddNewVar("ECVS_MODULE", "")
        self.AddNewVar("ECVS_TOD_DIR", "$DIST/")
        self.AddNewVar("S", "${WORKDIR}/${PN/-cvs/}")
        self.AddCommand("inherit cvs")
        self.AddFunc("src_compile", (src_compile))
        self.AddFunc("src_install", (src_install))

    def OnMnuEclassDistutils(self, event):
        if not self.editing:
            return

        # You don't need src_install() with distutils because it gets called automatically.
        # We add it in case they want to add anything to it.

        src_install = "src_install() {\n" + \
        "\tdistutils_src_install\n" + \
        "}"

        self.AddCommand("inherit distutils")
        self.AddFunc("src_install", (src_install))

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

    def AddEditor(self, name, val):
        """Add page in notebook for an editor"""
        n = panels.Editor(self.nb, self.sb, self.pref)
        self.editorList.append(n)
        self.nb.AddPage(n, name)
        n.editorCtrl.SetText(val)
        self.nb.SetSelection(self.nb.GetPageCount() -1)

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
            defaultVars = self.getDefaultVars()
            self.WriteEbuild()
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
            self.ClearNotebook()
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
            self.AddPages()
            self.panelMain.PopulateDefault()
            self.panelMain.SetURI(self.URI)
            #print 'seturi'
            self.panelMain.SetName(self.URI)
            #print 'setname'
            self.panelMain.SetPackage()
            #print 'setebuild'
            self.panelChangelog.Populate(filename= portdir + '/skel.ChangeLog')
            #We are in the middle of createing an ebuild. Should probably check for
            #presence of wxNotebook instead
            self.editing = 1
            if self.URI == "CVS" or self.URI == "cvs":
                self.OnMnuEclassCVS(-1)
            # Set titlebar of app to ebuild name
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

    def getDefaultVars(self):
        """Gather default variables from Main form"""
        defaultVars = {}
        defaultVars['package'] = self.panelMain.Package.GetValue()
        defaultVars['ebuild_file'] = self.panelMain.EbuildFile.GetValue()
        defaultVars['DESCRIPTION'] = self.panelMain.Desc.GetValue()
        defaultVars['HOMEPAGE'] = self.panelMain.Homepage.GetValue()
        defaultVars['SRC_URI'] = self.panelMain.URI.GetValue()
        defaultVars['LICENSE'] = self.panelMain.License.GetValue()
        defaultVars['SLOT'] = self.panelMain.Slot.GetValue()
        defaultVars['KEYWORDS'] = self.panelMain.Keywords.GetValue()
        defaultVars['S'] = self.panelMain.S.GetValue()
        defaultVars['IUSE'] = self.panelMain.USE.GetValue()
        defaultVars['DEPEND'] = self.panelDepend.elb1.GetStrings()
        defaultVars['RDEPEND'] = self.panelDepend.elb2.GetStrings()
        if defaultVars.has_key('S'):
            pass
        else:
            defaultVars['S'] = "S=${WORKDIR}/${P}"
        defaultVars['changelog'] = self.panelChangelog.edChangelog.GetText()
        return defaultVars

    def GetCategory(self):
        """Return category of ebuild"""
        categoryDir = os.path.join (portdir_overlay, self.panelMain.Category.GetValue())
        return categoryDir

    def isDefault(self, var):
        """ Return 1 if varibale is in list of default ebuild variables"""
        for l in defaults:
            if var == l:
                return 1

    def WriteEbuild(self):
        """Format data into fields and output to ebuild file"""
        categoryDir = self.GetCategory()
        if not os.path.exists(categoryDir):
            os.mkdir(categoryDir)
        self.ebuildDir = os.path.join (categoryDir, self.panelMain.Package.GetValue())
        if not os.path.exists(self.ebuildDir):
            os.mkdir(self.ebuildDir)
        filename = os.path.join(self.ebuildDir, self.panelMain.EbuildFile.GetValue())
        self.SetFilename(filename)
        self.filehistory.AddFileToHistory(filename.strip())
        f = open(filename, 'w')
        f.write('# Copyright 1999-2003 Gentoo Technologies, Inc.\n')
        f.write('# Distributed under the terms of the GNU General Public License v2\n')
        # Heh. CVS fills this line in, have to trick it with:
        f.write('# ' + '$' + 'Header:' + ' $\n')

        #Misc statements
        f.write('\n')
        t = self.panelMain.stext.GetValue()
        if t:
            f.write(t + '\n')
            f.write('\n')

        #Misc variables
        varList = self.panelMain.GetVars()
        for n in range(len(self.varOrder)):
            if not self.isDefault(self.varOrder[n]):
                f.write(self.varOrder[n] + '=' + varList[self.varOrder[n]].GetValue() + '\n')

        #TODO: Write these in the order they were imported? Or keep like in skel.ebuild?
        # This would print them in original order imported:
        #for n in range(len(self.varOrder)):
        #    if self.isDefault(self.varOrder[n]):
        #        f.write(self.varOrder[n] + '=' + varList[self.varOrder[n]].GetValue() + '\n')

        #Default variables
        f.write('S=' + self.panelMain.S.GetValue() + '\n')
        f.write('DESCRIPTION=' + self.panelMain.Desc.GetValue() + '\n')
        f.write('HOMEPAGE=' + self.panelMain.Homepage.GetValue() + '\n')
        f.write('SRC_URI=' + self.panelMain.URI.GetValue() + '\n')
        f.write('LICENSE=' + self.panelMain.License.GetValue() + '\n')
        f.write('SLOT=' + self.panelMain.Slot.GetValue() + '\n')
        f.write('KEYWORDS=' + self.panelMain.Keywords.GetValue() + '\n')
        f.write('IUSE=' + self.panelMain.USE.GetValue() + '\n')

        dlist = self.panelDepend.elb1.GetStrings()
        depFirst = 1 # Do we write DEPEND or RDEPEND first?
        d = 'DEPEND="'
        for ds in dlist:
            if ds == '${RDEPEND}':
                depFirst = 0
            if d == 'DEPEND="':
                d += ds + "\n"
            else:
                d += '\t' + ds + "\n"
        d = string.strip(d)
        d += '"'
        if d == 'DEPEND=""':
            d = ''
            f.write('\n')
        rdlist = self.panelDepend.elb2.GetStrings()
        rd = 'RDEPEND="'
        for ds in rdlist:
            if rd == 'RDEPEND="':
                rd += ds + "\n"
            else:
                rd += "\t" + ds + "\n"
        rd = string.strip(rd)
        rd += '"'
        if rd == 'RDEPEND=""':
            rd = ''
        if depFirst:
            if d:
                f.write(d + '\n')
            if rd:
                f.write(rd + '\n')
        else:
            if rd and d:
                f.write(rd + '\n')
                f.write(d + '\n')
        f.write('\n')

        #Write functions:
        for fun in self.funcList:
            ftext = fun.edNewFun.GetText()
            f.write(ftext + '\n')
        f.close()

        # Mark functions as saved
        for fns in self.funcList:
            fns.edNewFun.SetSavePoint()

        #TODO: We need to get each notebook's tab/label for this:
        #for n in range(len(self.funcOrder)):
        #    self.AddFunc(self.funcOrder[n], funcs[self.funcOrder[n]])

        self.AddEditor('Saved File', open(self.filename, 'r').read())

        changelog = os.path.join(self.ebuildDir, 'ChangeLog')
        f = open(changelog, 'w')
        f.write(self.panelChangelog.edChangelog.GetText())
        f.close()
        self.recentList.append(filename)

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
