#!/usr/bin/env python

"""Abeni - Gentoo Linux Ebuild Editor/Syntax Checker
Released under the terms of the GNU Public License v2
"""

__author__ = 'Rob Cakebread'
__version__ = '0.0.2'

from wxPython.wx import *
from wxPython.help import *
from wxPython.lib.dialogs import wxScrolledMessageDialog
import os, os.path, string, sys, re, urlparse
import panels, options

#Directory Abeni was started from
appdir = os.path.abspath(os.path.join(os.getcwd(), sys.path[0]))

class MyFrame(wxFrame):

    """ Main frame that holds the menu, toolbar and notebook """

    def __init__(self, parent, id, title):
        wxFrame.__init__(self, parent, -1, title, size=wxSize(800,480))
        self.SetAutoLayout(true)
        # Are we in the process of editing an ebuild?
        self.editing = 0
        # Get options from ~/.abeni/abenirc file
        #TODO: Its in /usr/share/abeni/abenirc, need to copy it to ~/ when first run
        self.GetOptions()
        # Custom functions added instances
        self.funcList = []
        #Misc editor tab instances
        self.editorList = []
        #Misc statements/commands instances
        self.statementList = []
        #application icon
        iconFile = ('/usr/share/bitmaps/abeni/mocha.png')
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
        menu_file = wxMenu()
        mnuNewID=wxNewId()
        menu_file.Append(mnuNewID, "&New")
        mnuLoadID=wxNewId()
        menu_file.Append(mnuLoadID, "&Load ebuild")
        EVT_MENU(self, mnuLoadID, self.OnMnuLoad)
        mnuSaveID=wxNewId()
        menu_file.Append(mnuSaveID, "&Save ebuild")
        EVT_MENU(self, mnuSaveID, self.OnMnuSave)
        mnuExitID=wxNewId()
        menu_file.Append(mnuExitID, "E&xit")
        EVT_MENU(self, mnuExitID, self.OnMnuExit)
        menubar = wxMenuBar()
        menubar.Append(menu_file, "&File")
        EVT_MENU(self, mnuNewID, self.OnMnuNew)
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
        # Tools
        menu_tools = wxMenu()
        mnuLintoolID = wxNewId()
        menu_tools.Append(mnuLintoolID, "Run &Lintool on this ebuild")
        EVT_MENU(self, mnuLintoolID, self.OnMnuLintool)
        mnuDigestID = wxNewId()
        menu_tools.Append(mnuDigestID, "&Create Digest")
        EVT_MENU(self, mnuDigestID, self.OnMnuCreateDigest)
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
        # TODO: Add for accelerator for each item in menu
        # Alt-X to exit
        aTable = wxAcceleratorTable([(wxACCEL_ALT,  ord('X'), mnuExitID)])
        self.SetAcceleratorTable(aTable)
        #Create Toolbar with icons
        newID = wxNewId()
        #closeID = wxNewId()
        openID = wxNewId()
        saveID = wxNewId()
        newVarID = wxNewId()
        newFunID = wxNewId()
        helpID = wxNewId()
        self.tb = self.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
        newBmp = ('/usr/share/bitmaps/abeni/new.bmp')
        saveBmp = ('/usr/share/bitmaps/abeni/save.bmp')
        openBmp = ('/usr/share/bitmaps/abeni/open.bmp')
        #closeBmp = ('/usr/share/bitmaps/abeni/close.bmp' % appdir)
        #newVarBmp = ('/usr/share/bitmaps/abeni/new_var.bmp')
        newVarBmp = ('/usr/share/bitmaps/abeni/x.png')
        #newFunBmp = ('/usr/share/bitmaps/abeni/new_fun.bmp')
        newFunBmp = ('/usr/share/bitmaps/abeni/fx.png')
        helpBmp = ('/usr/share/bitmaps/abeni/help.bmp')
        self.tb.AddSimpleTool(newID, wxBitmap(newBmp, wxBITMAP_TYPE_BMP), \
                                "Create new ebuild", "Create New ebuild")
        EVT_TOOL(self, newID, self.OnMnuNew)
        self.tb.AddSimpleTool(openID, wxBitmap(openBmp, wxBITMAP_TYPE_BMP), \
                                "Open ebuild", "Open ebuild")
        EVT_TOOL(self, openID, self.OnMnuLoad)
        self.tb.AddSimpleTool(saveID, wxBitmap(saveBmp, wxBITMAP_TYPE_BMP), \
                                "Save ebuild", "Save ebuild")
        EVT_TOOL(self, saveID, self.OnMnuSave)
        #self.tb.AddSimpleTool(closeID, wxBitmap(closeBmp, wxBITMAP_TYPE_BMP), \
        #                        "Close ebuild", "Close ebuild")
        self.tb.AddSimpleTool(newVarID, wxBitmap(newVarBmp, wxBITMAP_TYPE_PNG), \
                                "New Variable", "New Variable")
        EVT_TOOL(self, newVarID, self.OnMnuNewVariable)
        self.tb.AddSimpleTool(newFunID, wxBitmap(newFunBmp, wxBITMAP_TYPE_PNG), \
                                "New Function", "New Function")
        EVT_TOOL(self, newFunID, self.OnMnuNewFunction)
        self.tb.AddSimpleTool(helpID, wxBitmap(helpBmp, wxBITMAP_TYPE_BMP ), \
                                "Help", "Abeni Help")
        EVT_TOOL(self, helpID, self.OnMnuHelp)
        self.tb.Realize()
        EVT_TOOL_ENTER(self, -1, self.OnToolZone)
        EVT_TIMER(self, -1, self.OnClearSB)
        self.timer = None

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
            print f
            for key in varList:
                if key.GetLabel() == f:
                    key.Destroy()
                    varList[key].Destroy()
                    del varList[key]
                    break
            #TODO: We need to redraw the variables on the GUI, it just leaves a
            # blank as it is now. Sizers don't seem to work if you destroy/rebuild them.
            # Or, more likely, I just don't know sizers yet.
        dlg.Destroy()

    def OnMnuCreateDigest(self, event):
        """Run 'ebuild filename digest' on this ebuild"""
        if not self.editing:
            return

        # I did this in an xterm because it has colored output.
        #TODO: Strip escape codes so we can put in a text widget

        cmd = '"ebuild ' + self.filename + ' digest' \
                  + ' && echo You can close this window now."'
        os.system('xterm -T "Creating Digest" -hold -e ' + cmd + ' &')


    def OnMnuLintool(self, event):
        """Run 'lintool' on this ebuild"""
        if not self.editing:
            return

        cmd = '"/usr/bin/lintool ' + self.filename \
                  + ' && echo You can close this window now."'
        os.system('xterm -T "Lintool" -hold -e ' + cmd + ' &')

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
        self.nb.RemovePage(self.nb.GetSelection())

    def ClearNotebook(self):
        """Delete all pages in the notebook"""
        self.nb.DeleteAllPages()
        self.funcList = []
        self.statementList = []
        self.editorList = []

    def SetFilename(self, filename):
        """Set the ebuild full path and filename"""
        self.filename = filename

    def GetFilename(self):
        """Get the full path and filename of ebuild"""
        return self.filename

    def OnMnuLoad(self, event):
        """Load ebuild file"""
        #TODO: Add an "Are you sure?" dialog
        # statements section
        # Comments: This is going to need a lot of work. I'll need to break up the
        #   ebuild into a tree, by vars, statements and functions, so I can put the
        #   comments back in the right place.
        if self.editing:
            self.ClearNotebook()
        wildcard = "ebuild files (*.ebuild)|*.ebuild"
        dlg = wxFileDialog(self, "Choose a file", "/usr/portage/", "", \
                            wildcard, wxOPEN)
        if dlg.ShowModal() == wxID_OK:
            filename = dlg.GetPath()
            self.SetFilename(filename)
            vars = {}
            funcs = {}
            statements = []
            f = open(filename, 'r')
            while 1:
                l = f.readline()
                if not l: #End of file
                    break
                if len(l) > 1:
                    l = string.strip(l)
                # Variables always start a line with all caps
                varTest = re.search('^[A-Z]', l)
                # Function like: mine() {   or mine ()
                funcTest1 = re.search('^[a-z]*\(\) {', l)
                funcTest2 = re.search('^[a-z]* \(\) {', l)
                # Function like: my_func() {   or  my_func ()
                funcTest3 = re.search('^[a-z]*_[a-z]*\(\) {', l)
                funcTest4 = re.search('^[a-z]*_[a-z]* \(\) {', l)
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

                    vars[s[0]] = string.replace(s[1], '"', '')
                    continue
                if funcTest1 or funcTest2 or funcTest3 or funcTest4:
                    tempf = []
                    fname = string.replace(l, "{", "")
                    tempf.append(l + "\n")
                    while 1:
                        l = f.readline()
                        tempf.append(l)
                        if l[0] == "}":
                            s = ""
                            for ls in tempf:
                                s += ls
                            funcs[fname] = s
                            break
                    continue
                # Command like 'inherit cvs'
                if re.search('^[a-z]', l):
                    self.statementList.append(l)
            f.close()

            #DEBUG
            #print "Statements: ", self.statementList

            s = string.split(filename, "/")
            ebuild_file = s[len(s)-1]
            ebuild = s[len(s)-2]
            category = s[len(s)-3]
            clog = string.replace(filename, ebuild_file, '') + 'ChangeLog'
            myData = {}
            otherVars = {}
            myData, otherVars = self.SeparateVars(vars)
            myData['ebuild'] = ebuild
            myData['ebuild_file'] = ebuild_file
            myData['category'] = category
            self.editing = 1
            self.AddPages()
            self.PopulateForms(myData)
            self.panelChangelog.Populate(clog)
            #Add custom variables to Main panel
            for v in otherVars:
                self.AddNewVar(v, otherVars[v])
            # Add function pages to notebook
            for fname in funcs:
                self.AddFunc(fname, funcs[fname])
            for s in self.statementList:
                self.panelMain.AddStatement(s)
            # Add original ebuild file:
            self.AddEditor('Original File', open(filename, 'r').read())
            self.nb.SetSelection(0)
            # Set titlebar of app to ebuild name
            self.SetTitle('Abeni ' + __version__ + ': ' + ebuild_file)
        dlg.Destroy()

    def PopulateForms(self, myData):
        """Fill forms with saved data"""
        self.panelMain.Ebuild.SetValue(myData['ebuild'])
        self.panelMain.EbuildFile.SetValue(myData['ebuild_file'])
        self.panelMain.Category.SetValue(myData['category'])
        self.panelMain.URI.SetValue(myData['SRC_URI'])
        self.panelMain.Homepage.SetValue(myData['HOMEPAGE'])
        self.panelMain.Desc.SetValue(myData['DESCRIPTION'])
        self.panelMain.USE.SetValue(myData['IUSE'])
        self.panelMain.Slot.SetValue(myData['SLOT'])
        self.panelMain.Keywords.SetValue(myData['KEYWORDS'])
        self.panelMain.License.SetValue(myData['LICENSE'])
        depends = string.split(myData['DEPEND'], '\n')
        self.panelDepend.elb1.SetStrings(depends)
        rdepends = string.split(myData['RDEPEND'], '\n')
        self.panelDepend.elb2.SetStrings(rdepends)

    def SeparateVars(self, vars):
        """Separates variables into defaults (myData) and all others (otherVars)"""
        l = ["SRC_URI", "HOMEPAGE", "DEPEND", "RDEPEND", "DESCRIPTION", "IUSE", "SLOT", "KEYWORDS", "LICENSE"]
        myData = {}
        for key in l:
            if vars.has_key(key):
                myData[key] = vars[key]
                del vars[key]
            else:
                myData[key] = ""
        return myData, vars

    def GetOptions(self):
        """Global options from apprc file"""
        myOptions = options.Options()
        self.pref = myOptions.Prefs()
        self.debug = self.pref['debug']

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

    def OnMnuNewVariable(self, event):
        """Dialog for adding new variable"""
        if not self.editing:
            return
        dlg = wxTextEntryDialog(self, 'New Variable Name:',
                            'Enter Variable Name', 'test')
        dlg.SetValue("")
        if dlg.ShowModal() == wxID_OK:
            newVariable = dlg.GetValue()
            self.AddNewVar(newVariable, "")
        dlg.Destroy()

    def AddNewVar(self, var, val):
        """Add new variable on Main panel"""
        self.panelMain.AddVar(var, val)

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
        #TODO: Fix index. Doesn't die when you exit.
        #Add: /usr/portage/profiles/use.desc
        #os.system("netscape '/usr/share/abeni/ebuild-quick-reference.html' &")
        os.system("netscape 'http://abeni.sf.net/docs/ebuild-quick-reference.html' &")

    def OnMnuHelp(self, event):
        """Display html help file"""
        #TODO: Fix index. Doesn't die when you exit.
        #Add: /usr/portage/profiles/use.desc
        #os.system("netscape '/usr/share/abeni/index.html' &")
        os.system("netscape 'http://abeni.sf.net/docs/index.html' &")

        #import glob
        #from wxPython.tools import helpviewer
        #if __name__ == '__main__':
        #    basePath = os.path.dirname(sys.argv[0])
        #else:
        #    basePath = os.path.dirname(__file__)
        # setup the args
        #args = ['',
        #        '--cache='+basePath,
        #        os.path.join(basePath, 'docs.zip'),
        #        ]

        # launch helpviewer
        #helpviewer.main(args)


    def OLD__OnMnuLoad(self, event):
        """Load raw data from pickled file"""
        # This will probably be removed, unless someone can think of a good reason to pickle everything
        # as well as save it in native ebuild files.
        wildcard = "Abeni files (*.abeni)|*.abeni"
        dlg = wxFileDialog(self, "Choose a file", "", "", wildcard, wxOPEN|wxMULTIPLE)
        if dlg.ShowModal() == wxID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                print path
        dlg.Destroy()
        file = open(path, 'r')
        myData = pickle.load(file)
        for myKeys in myData.keys():
            print myData[myKeys]
        self.URI = myData['SRC_URI']
        self.AddPages()
        self.PopulateForms(myData)
        self.editing = 1

    def OnMnuSave(self, event):
        """Save ebuild file to disk"""
        if not self.editing:
            return
        if self.checkEntries():
            myData = self.GatherData()
            #This is for pickling data:
            #file = open(self.panelMain.Ebuild.GetValue() + ".abeni", 'w')
            #pickle.dump(myData, file)
            self.WriteEbuild()
        #TODO: dialog showing save failed

    def checkEntries(self):
        """Validate entries on forms"""
        # TODO: some sanity checking here
        return 1

    def OnMnuNew(self,event):
        """Creates a new ebuild from scratch"""
        #TODO: Add an "Are you sure?" dialog
        if self.editing:
            self.ClearNotebook()
        win = GetURIDialog(self, -1, "Enter Package URI", \
                            size=wxSize(350, 200), \
                            style = wxDEFAULT_DIALOG_STYLE \
                            )
        win.CenterOnScreen()
        val = win.ShowModal()
        self.URI = win.URI.GetValue()
        # If they click OK and filled out URI entry, create notebook
        if val == wxID_OK and self.URI:
            self.AddPages()
            self.panelMain.PopulateDefault()
            self.panelMain.SetURI(self.URI)
            self.panelMain.SetName(self.URI)
            self.panelMain.SetEbuild()
            self.panelChangelog.Populate(filename='/usr/portage/skel.ChangeLog')
            #We are in the middle of createing an ebuild. Should probably check for
            #presence of wxNotebook instead
            self.editing = 1
            # Set titlebar of app to ebuild name
            self.SetTitle("Abeni " + __version__ + ": " + self.panelMain.GetEbuildName())

    def AddPages(self):
        """Add pages to blank notebook"""
        self.panelMain=panels.main(self.nb, self.sb, self.pref)
        self.panelDepend=panels.depend(self.nb, self.sb, self.pref)
        self.panelChangelog=panels.changelog(self.nb, self.sb, self.pref)
        self.nb.AddPage(self.panelMain, "Main")
        self.nb.AddPage(self.panelDepend, "Dependencies")
        self.nb.AddPage(self.panelChangelog, "ChangeLog")

    def OnMnuExit(self,event):
        """Exits and closes application"""
        self.Close()

    def OnMnuPref(self, event):
        """Global preferences entry dialog"""
        import OptionFrame
        dlg = OptionFrame.OptionFrame(None, -1, "Global Preferences")
        dlg.Show(true)

    def OnMnuAbout(self,event):
        """Obligitory About me and my app screen"""
        dlg = wxMessageDialog(self, 'Abeni ' + __version__ + ' is a Python and wxPython application\n \
            by Rob Cakebread released under the GPL license.\n\n', \
                              'About Abeni ' + __version__, wxOK | wxICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def GatherData(self):
        """Gather data from form"""
        myData = {}
        myData['ebuild'] = self.panelMain.Ebuild.GetValue()
        myData['ebuild_file'] = self.panelMain.EbuildFile.GetValue()
        myData['DESCRIPTION'] = self.panelMain.Desc.GetValue()
        myData['HOMEPAGE'] = self.panelMain.Homepage.GetValue()
        myData['SRC_URI'] = self.panelMain.URI.GetValue()
        myData['LICENSE'] = self.panelMain.License.GetValue()
        myData['SLOT'] = self.panelMain.Slot.GetValue()
        myData['KEYWORDS'] = self.panelMain.Keywords.GetValue()
        myData['IUSE'] = self.panelMain.USE.GetValue()
        myData['DEPEND'] = self.panelDepend.elb1.GetStrings()
        myData['RDEPEND'] = self.panelDepend.elb2.GetStrings()
        #myData['S'] = "S=${WORKDIR}/${P}"
        myData['changelog'] = self.panelChangelog.edChangelog.GetText()
        return myData

    def WriteEbuild(self):
        """Format data into fields and output to ebuild file"""
        #abeniPath = os.path.join(os.path.expanduser('~'), '.abeni')
        #if not os.path.exists(abeniPath):
        #    os.mkdir(abeniPath)
        categoryDir = os.path.join ('/usr/local/portage', self.panelMain.Category.GetValue())
        if not os.path.exists(categoryDir):
            os.mkdir(categoryDir)
        ebuildDir = os.path.join (categoryDir, self.panelMain.Ebuild.GetValue())
        if not os.path.exists(ebuildDir):
            os.mkdir(ebuildDir)
        filename = os.path.join(ebuildDir, self.panelMain.EbuildFile.GetValue())
        self.SetFilename(filename)
        f = open(filename, 'w')

        f.write('# Copyright 1999-2003 Gentoo Technologies, Inc.\n')
        f.write('# Distributed under the terms of the GNU General Public License v2\n')
        f.write('# $Header: /cvsroot/abeni/abeni/Attic/abeni.py,v 1.22 2003/06/05 08:08:06 robc Exp $\n\n')

        f.write(self.panelMain.stext.GetValue() + '\n')
        varList = self.panelMain.GetVars()
        for key in varList.keys():
            #f.write(textList[i] + '="' + varList[i].GetValue() + '"\n')
            f.write(key.GetLabel() + '="' + varList[key].GetValue() + '"\n')

        #f.write("S=${WORKDIR}/${P}\n\n")
        f.write('DESCRIPTION="' + self.panelMain.Desc.GetValue() + '"\n')
        f.write('HOMEPAGE="' + self.panelMain.Homepage.GetValue() + '"\n')
        f.write('SRC_URI="' + self.panelMain.URI.GetValue() + '"\n')
        f.write('LICENSE="' + self.panelMain.License.GetValue() + '"\n')
        f.write('SLOT="' + self.panelMain.Slot.GetValue() + '"\n')
        f.write('KEYWORDS="' + self.panelMain.Keywords.GetValue() + '"\n')
        f.write('IUSE="' + self.panelMain.USE.GetValue() + '"\n')
        dlist = self.panelDepend.elb1.GetStrings()
        d = 'DEPEND="'
        for ds in dlist:
            if d == 'DEPEND="':
                d += ds + "\n"
            else:
                d += '\t' + ds + "\n"
        d = string.strip(d)
        d += '"'
        rdlist = self.panelDepend.elb2.GetStrings()
        rd = 'RDEPEND="'
        for ds in rdlist:
            if rd == 'RDEPEND="':
                rd += ds + "\n"
            else:
                rd += "\t" + ds + "\n"
        rd = string.strip(rd)
        rd += '"'
        f.write(d + '\n\n')
        f.write(rd + '\n\n')

        #Write functions:
        for fun in self.funcList:
            ftext = fun.edNewFun.GetText()
            f.write(ftext + '\n')
        f.close()
        self.AddEditor('Saved File', open(self.filename, 'r').read())

        changelog = os.path.join(ebuildDir, 'ChangeLog')
        f = open(changelog, 'w')
        f.write(self.panelChangelog.edChangelog.GetText())
        f.close()


class GetURIDialog(wxDialog):

    """Dialog box that pops up for URI"""

    def __init__(self, parent, ID, title,
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxDEFAULT_DIALOG_STYLE):
        # Instead of calling wxDialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI dialog using the Create
        # method.
        pre = wxPreDialog()
        pre.SetExtraStyle(wxDIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.this = pre.this
        sizer = wxBoxSizer(wxVERTICAL)
        box = wxBoxSizer(wxHORIZONTAL)
        label = wxStaticText(self, -1, "Package URI:")
        label.SetHelpText("Enter the URI for the package. This can be a URL like 'http://..' or a path to a file.")
        box.Add(label, 0, wxALIGN_CENTRE|wxALL, 5)
        self.URI = wxTextCtrl(self, -1, "http://abeni.sf.net/abeni-1.2.3.tgz", size=(280,-1))
        self.URI.SetHelpText("Enter the URI for the package. This can be a URL like 'http://...' or a path to a file.")
        box.Add(self.URI, 1, wxALIGN_CENTRE|wxALL, 5)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        box = wxBoxSizer(wxHORIZONTAL)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        sizer.Add(line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxRIGHT|wxTOP, 5)
        box = wxBoxSizer(wxHORIZONTAL)
        btn = wxButton(self, wxID_OK, " OK ")
        btn.SetDefault()
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        btn = wxButton(self, wxID_CANCEL, " Cancel ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        btn = wxContextHelpButton(self)
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        sizer.AddSizer(box, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)


class MyApp(wxApp):

    """ Main wxPython app class """

    def OnInit(self):
        """Set up the main frame"""
        provider = wxSimpleHelpProvider()
        wxHelpProvider_Set(provider)
        # Enable gif, jpg, bmp, png handling for wxHtml and icons
        wxInitAllImageHandlers()
        frame=MyFrame(None, -1, 'Abeni - The ebuild Builder ' + __version__)
        frame.Show(true)
        self.SetTopWindow(frame)
        return true

app=MyApp(0)
app.MainLoop()
