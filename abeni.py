#!/usr/bin/env python

"""Abeni - by Rob Cakebread
Released under the terms of the GNU Public License v2
"""

__author__ = 'Rob Cakebread'
__version__ = '0.0.1'
from wxPython.wx import *
from wxPython.help import *
import os, os.path, string, sys, re, urlparse
import panels, options

#Find directory Abeni was started from
appdir = os.path.abspath(os.path.join(os.getcwd(), sys.path[0]))

class MyFrame(wxFrame):

    """ Main frame that holds the menu, toolbar and notebook """

    def __init__(self, parent, id, title):
        wxFrame.__init__(self, parent, -1, title, size=wxSize(800,480))
        self.SetAutoLayout(true)
        # Are we in the process of editing an ebuild?
        self.editing = 0
        # Get options from ~/.abeni/abenirc file
        self.GetOptions()
        # Custom functions added
        self.funcList = []
        #application icon
        iconFile = ('%s/Images/mocha.png' % appdir)
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
        mnuSaveID=wxNewId()
        menu_file.Append(mnuSaveID, "&Save ebuild")
        mnuExitID=wxNewId()
        menu_file.Append(mnuExitID, "E&xit")
        menubar = wxMenuBar()
        menubar.Append(menu_file, "&File")
        EVT_MENU(self, mnuExitID, self.OnMnuExit)
        EVT_MENU(self, mnuSaveID, self.OnMnuSave)
        EVT_MENU(self, mnuLoadID, self.OnMnuLoad)
        EVT_MENU(self, mnuNewID, self.OnMnuNew)
        # Edit
        menu_edit = wxMenu()
        mnuNewVariableID = wxNewId()
        mnuNewFunctionID = wxNewId()
        mnuDelFunctionID = wxNewId()
        menu_edit.Append(mnuNewVariableID, "New &Variable")
        menu_edit.Append(mnuNewFunctionID, "New &Function")
        menu_edit.Append(mnuDelFunctionID, "&Delete Function")
        menubar.Append(menu_edit, "&Edit")
        EVT_MENU(self, mnuNewVariableID, self.OnMnuNewVariable)
        EVT_MENU(self, mnuNewFunctionID, self.OnMnuNewFunction)
        EVT_MENU(self, mnuDelFunctionID, self.OnMnuDelFunction)
        # Options
        menu_options = wxMenu()
        mnuPrefID = wxNewId()
        menu_options.Append(mnuPrefID, "&Global Preferences")
        menubar.Append(menu_options, "&Options")
        EVT_MENU(self, mnuPrefID, self.OnMnuPref)
        # Help
        menu_help = wxMenu()
        mnuHelpID = wxNewId()
        mnuAboutID = wxNewId()
        menu_help.Append(mnuHelpID,"&Contents")
        menu_help.Append(mnuAboutID,"&About")
        menubar.Append(menu_help,"&Help")
        self.SetMenuBar(menubar)
        EVT_MENU(self, mnuAboutID, self.OnMnuAbout)
        EVT_MENU(self, mnuHelpID, self.OnMnuHelp)
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
        newBmp = ('%s/Images/new.bmp' % appdir)
        saveBmp = ('%s/Images/save.bmp' % appdir)
        openBmp = ('%s/Images/open.bmp' % appdir)
        #closeBmp = ('%s/Images/close.bmp' % appdir)
        newVarBmp = ('%s/Images/new_var.bmp' % appdir)
        newFunBmp = ('%s/Images/new_fun.bmp' % appdir)
        helpBmp = ('%s/Images/help.bmp' % appdir)
        self.tb.AddSimpleTool(newID, wxBitmap(newBmp, wxBITMAP_TYPE_BMP), \
                                "Create new ebuild", "Create New ebuild")
        self.tb.AddSimpleTool(openID, wxBitmap(openBmp, wxBITMAP_TYPE_BMP), \
                                "Open ebuild", "Open ebuild")
        self.tb.AddSimpleTool(saveID, wxBitmap(saveBmp, wxBITMAP_TYPE_BMP), \
                                "Save ebuild", "Save ebuild")
        #self.tb.AddSimpleTool(closeID, wxBitmap(closeBmp, wxBITMAP_TYPE_BMP), \
        #                        "Close ebuild", "Close ebuild")
        self.tb.AddSimpleTool(newVarID, wxBitmap(newVarBmp, wxBITMAP_TYPE_BMP), \
                                "New Variable", "New Variable")
        self.tb.AddSimpleTool(newFunID, wxBitmap(newFunBmp, wxBITMAP_TYPE_BMP), \
                                "New Function", "New Function")
        self.tb.AddSimpleTool(helpID, wxBitmap(helpBmp, wxBITMAP_TYPE_BMP ), \
                                "Help", "Abeni Help")
        self.tb.Realize()
        EVT_TOOL(self, newID, self.OnMnuNew)
        EVT_TOOL(self, openID, self.OnMnuLoad)
        EVT_TOOL(self, newVarID, self.OnMnuNewVariable)
        EVT_TOOL(self, newFunID, self.OnMnuNewFunction)
        EVT_TOOL(self, saveID, self.OnMnuSave)
        #EVT_TOOL(self, openID, self.OnMnuOpen)
        EVT_TOOL_ENTER(self, -1, self.OnToolZone)
        EVT_TIMER(self, -1, self.OnClearSB)
        self.timer = None

    def OnMnuDelFunction(self, event):
        """Remove current function page"""
        self.nb.RemovePage(self.nb.GetSelection())

    def ClearNotebook(self):
        """Delete all pages in the notebook"""
        self.nb.DeleteAllPages()
        self.funcList=[]

    def OnMnuLoad(self, event):
        """Load ebuild file"""
        #TODO: Add an "Are you sure?" dialog
        # Multi-line variables now work, so DEPEND/RDEPEND can be done now.
        # Commands/statements section
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
            vars = {}
            funcs = {}
            commands = []
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
                # Command like rm -rf /tmp/foo
                if re.search('^[a-z]', l):
                    commands.append(l)
            f.close()
            #DEBUG
            print "COMMANDS:\n"
            print commands
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
            # Add original ebuild file:
            self.AddFunc('Original File', open(filename, 'r').read())
            self.nb.SetSelection(0)
            # Set titlebar of app to ebuild name
            self.SetTitle('Abeni: ' + ebuild_file)
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

    def OnMnuHelp(self, event):
        """Display html help file"""
        #TODO: Fix index. Doesn't die when you exit.
        #Add: /usr/portage/profiles/use.desc
        import glob
        from wxPython.tools import helpviewer
        if __name__ == '__main__':
            basePath = os.path.dirname(sys.argv[0])
        else:
            basePath = os.path.dirname(__file__)
        # setup the args
        args = ['',
                '--cache='+basePath,
                os.path.join(basePath, 'docs.zip'),
                ]

        # launch helpviewer
        helpviewer.main(args)


    def OnOLDMnuLoad(self, event):
        """Load raw data from pickled file"""
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
            self.FormatEbuild()
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
            self.SetTitle("Abeni: " + self.panelMain.GetEbuildName())

    def AddPages(self):
        """Add pages to blank notebook"""
        self.panelMain=panels.main(self.nb, self.sb, self.pref)
        self.panelDepend=panels.depend(self.nb, self.sb, self.pref)
        self.panelChangelog=panels.changelog(self.nb, self.sb, self.pref)
        self.nb.AddPage(self.panelMain, "Main")
        self.nb.AddPage(self.panelDepend, "Dependencies")
        self.nb.AddPage(self.panelChangelog, "ChangeLog")

    def OnMnuNewFrom(self,event):
        """Create new ebuild, copying existing ebuild"""
        pass

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
        dlg = wxMessageDialog(self, 'Abeni is a Python and wxPython application\n \
            by Rob Cakebread released under the GPL license.\n\n', \
                              'About Abeni', wxOK | wxICON_INFORMATION)
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

    def FormatEbuild(self):
        """Format data into fields ready to output to ebuild file"""
        #abeniPath = os.path.join(os.path.expanduser('~'), '.abeni')
        #if not os.path.exists(abeniPath):
        #    os.mkdir(abeniPath)
        categoryDir = os.path.join ('/usr/local/portage', self.panelMain.Category.GetValue())
        if not os.path.exists(categoryDir):
            os.mkdir(categoryDir)
        ebuildDir = os.path.join (categoryDir, self.panelMain.Ebuild.GetValue())
        if not os.path.exists(ebuildDir):
            os.mkdir(ebuildDir)
        ebuildFile = os.path.join(ebuildDir, self.panelMain.EbuildFile.GetValue())
        f = open(ebuildFile, 'w')

        textList, varList = self.panelMain.GetVars()
        for i in range(0, len(varList)):
            f.write(textList[i] + '="' + varList[i].GetValue() + '"\n\n')

        #f.write("S=${WORKDIR}/${P}\n\n")
        f.write('DESCRIPTION="' + self.panelMain.Desc.GetValue() + '"\n\n')
        f.write('HOMEPAGE="' + self.panelMain.Homepage.GetValue() + '"\n\n')
        f.write('SRC_URI="' + self.panelMain.URI.GetValue() + '"\n\n')
        f.write('LICENSE="' + self.panelMain.License.GetValue() + '"\n\n')
        f.write('SLOT="' + self.panelMain.Slot.GetValue() + '"\n\n')
        f.write('KEYWORDS="' + self.panelMain.Keywords.GetValue() + '"\n\n')
        f.write('IUSE="' + self.panelMain.USE.GetValue() + '"\n\n')
        dlist = self.panelDepend.elb1.GetStrings()
        d = 'DEPEND="'
        for ds in dlist:
            if d == 'DEPEND="':
                d += ds + "\n"
            else:
                d += '   ' + ds + "\n"
        d = string.strip(d)
        d += '"'
        rdlist = self.panelDepend.elb2.GetStrings()
        rd = 'RDEPEND="'
        for ds in rdlist:
            if rd == 'RDEPEND="':
                rd += ds + "\n"
            else:
                rd += "   " + ds + "\n"
        rd = string.strip(rd)
        rd += '"'
        f.write(d + '\n\n')
        f.write(rd + '\n\n')

        #Write functions:
        for fun in self.funcList:
            ftext = fun.edNewFun.GetText()
            f.write(ftext + '\n')

        #CHANGELOG.write(self.panelChangelog.ed.GetText())


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
        frame=MyFrame(None, -1, 'Abeni - The ebuild Builder')
        frame.Show(true)
        self.SetTopWindow(frame)
        return true

app=MyApp(0)
app.MainLoop()
