#!/usr/bin/env python

"""Abeni - by Rob Cakebread
Released under the terms of the GNU Public License v2"""

__author__ = 'Rob Cakebread'
__version__ = '0.0.1'

from wxPython.wx import *
from wxPython.help import *
import os, os.path, string, shutil, time, sys, pickle
import panels, options

#Find directory Abeni was started from
appdir = os.path.abspath(os.path.join(os.getcwd(), sys.path[0]))

# Enable gif, jpg, bmp, png handling for wxHtml and icons
wxInitAllImageHandlers()


class MyFrame(wxFrame):

    """ Main frame that holds the menu, toolbar and notebook """

    def __init__(self, parent, id, title):
        wxFrame.__init__(self, parent, -1, title, size=wxSize(800,480))
        self.SetAutoLayout(true)

        # Are we in the process of editing an ebuild?
        self.editing = 0

        # Get options from abenirc file
        self.GetOptions()

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
        mnuNewFromID=wxNewId()
        menu_file.Append(mnuNewFromID, "New &From Existing ebuild")
        mnuLoadID=wxNewId()
        menu_file.Append(mnuLoadID, "&Load ebuild")
        mnuSaveID=wxNewId()
        menu_file.Append(mnuSaveID, "&Save ebuild")
        mnuExitID=wxNewId()
        menu_file.Append(mnuExitID, "E&xit")
        menubar = wxMenuBar()
        menubar.Append(menu_file, "&File")

        # Edit
        menu_edit = wxMenu()
        mnuEditID = wxNewId()
        menu_edit.Append(mnuEditID, "&New Variable")
        menubar.Append(menu_edit, "&Edit")

        # Options
        menu_options = wxMenu()
        mnuPrefID = wxNewId()
        menu_options.Append(mnuPrefID, "&Global Preferences")
        menubar.Append(menu_options, "&Options")

        # Help
        menu_help = wxMenu()
        mnuHelpID = wxNewId()
        mnuAboutID = wxNewId()
        menu_help.Append(mnuHelpID,"&Contents")
        menu_help.Append(mnuAboutID,"&About")
        menubar.Append(menu_help,"&Help")
        self.SetMenuBar(menubar)
        EVT_MENU(self, mnuExitID, self.OnMnuExit)
        EVT_MENU(self, mnuSaveID, self.OnMnuSave)
        EVT_MENU(self, mnuLoadID, self.OnMnuLoad)
        EVT_MENU(self, mnuNewID, self.OnMnuNew)
        EVT_MENU(self, mnuNewFromID, self.OnMnuNewFrom)
        EVT_MENU(self, mnuEditID, self.OnMnuNewVariable)
        EVT_MENU(self, mnuPrefID, self.OnMnuPref)
        EVT_MENU(self, mnuAboutID, self.OnMnuAbout)
        EVT_MENU(self, mnuHelpID, self.OnMnuHelp)

        # Keyboard accelerators
        # TODO: Add for accelerator for each item in menu

        # Alt-X to exit
        aTable = wxAcceleratorTable([(wxACCEL_ALT,  ord('X'), mnuExitID)])
        self.SetAcceleratorTable(aTable)

        #Create Toolbar with icons

        newID = wxNewId()
        closeID = wxNewId()
        helpID = wxNewId()
        self.tb = self.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
        newBmp = ('%s/Images/new.bmp' % appdir)
        closeBmp = ('%s/Images/close.bmp' % appdir)
        helpBmp = ('%s/Images/help.bmp' % appdir)
        self.tb.AddSimpleTool(newID, wxBitmap(newBmp, wxBITMAP_TYPE_BMP), \
                                "Create new ebuild", "Create New ebuild")
        self.tb.AddSimpleTool(closeID, wxBitmap(closeBmp, wxBITMAP_TYPE_BMP), \
                                "Close ebuild", "Close ebuild")
        self.tb.AddSimpleTool(helpID, wxBitmap(helpBmp, wxBITMAP_TYPE_BMP ), \
                                "Help", "Abeni Help")
        self.tb.Realize()
        EVT_TOOL(self, newID, self.OnMnuNew)
        EVT_TOOL_ENTER(self, -1, self.OnToolZone)
        EVT_TIMER(self, -1, self.OnClearSB)
        self.timer = None

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
        event.Skip()
        self.nbPage = event.GetSelection()

    def OnMnuNewVariable(self, event):
        """Add new variable to Main panel"""
        dlg = wxTextEntryDialog(self, 'New Variable Name:',
                            'Enter Variable Name', 'test')
        dlg.SetValue("")
        if dlg.ShowModal() == wxID_OK:
            newVariable = dlg.GetValue()
            self.panelMain.AddVar(newVariable)
        dlg.Destroy()


    def OnMnuHelp(self, event):
        """Display html help file"""
        pass

    def OnMnuLoad(self, event):
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
        self.URI = myData['src_uri']
        self.AddPages()
        self.PopulateForms(myData)
        self.editing = 1

    def PopulateForms(self, myData):
        """Fill forms with saved data"""
        self.panelMain.Ebuild.SetValue(myData['ebuild'])
        self.panelMain.EbuildFile.SetValue(myData['ebuild_file'])
        self.panelMain.URI.SetValue(myData['src_uri'])
        self.panelMain.Rev.SetValue(myData['rev'])
        self.panelMain.Homepage.SetValue(myData['homepage'])
        self.panelMain.Desc.SetValue(myData['desc'])
        self.panelMain.USE.SetValue(myData['iuse'])
        self.panelMain.Slot.SetValue(myData['slot'])
        self.panelMain.Keywords.SetValue(myData['keywords'])

    def OnMnuSave(self, event):
        """Save ebuild file to disk"""
        if self.checkEntries():
            myData = self.GatherData()
            file = open(self.panelMain.Ebuild.GetValue() + ".abeni", 'w')
            pickle.dump(myData, file)
        self.FormatEbuild()

    def checkEntries(self):
        """Validate entries on forms"""
        # Do some sanity checking here
        return 1

    def OnMnuNew(self,event):
        """Creates a new ebuild from scratch"""
        if not self.editing:
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
                #We are in the middle of createing an ebuild. Should probably check for
                #presence of wxNotebook instead
                self.editing = 1
                # Set titlebar of app to ebuild name
                self.SetTitle(self.panelMain.GetEbuildName())

    def AddPages(self):
        """Add pages to blank notebook"""
        self.panelMain=panels.main(self.nb, self.sb, self.pref)
        self.panelDepend=panels.depend(self.nb, self.sb, self.pref)
        self.panelCompile=panels.compile(self.nb, self.sb, self.pref)
        self.panelInstall=panels.install(self.nb, self.sb, self.pref)
        self.panelChangelog=panels.changelog(self.nb, self.sb, self.pref)
        self.nb.AddPage(self.panelMain, "Main")
        self.nb.AddPage(self.panelDepend, "Dependencies")
        self.nb.AddPage(self.panelCompile, "Compile")
        self.nb.AddPage(self.panelInstall, "Install")
        self.nb.AddPage(self.panelChangelog, "Changelog")

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
        myData['desc'] = self.panelMain.Desc.GetValue()
        myData['homepage'] = self.panelMain.Homepage.GetValue()
        myData['src_uri'] = self.panelMain.URI.GetValue()
        myData['rev'] = self.panelMain.Rev.GetValue()
        myData['license'] = self.panelMain.License
        myData['slot'] = self.panelMain.Slot.GetValue()
        myData['keywords'] = self.panelMain.Keywords.GetValue()
        myData['iuse'] = self.panelMain.USE.GetValue()
        myData['depend'] = self.panelDepend.elb1.GetStrings()
        myData['rdepend'] = self.panelDepend.elb2.GetStrings()
        myData['s'] = "S=${WORKDIR}/${P}"
        myData['src_compile'] = self.panelCompile.ed.GetText()
        myData['src_install'] = self.panelInstall.ed.GetText()
        myData['changelog'] = self.panelChangelog.ed.GetText()
        return myData

    def FormatEbuild(self):
        """Format data into fields ready to output to ebuild file"""
        abeniPath = os.path.join(os.path.expanduser('~'), '.abeni')
        if not os.path.exists(abeniPath):
            os.mkdir(abeniPath)
        ebuildDir = os.path.join (abeniPath, self.panelMain.Ebuild.GetValue())
        if not os.path.exists(ebuildDir):
            os.mkdir(ebuildDir)
        ebuildFile = os.path.join(ebuildDir, self.panelMain.EbuildFile.GetValue())
        f = open(ebuildFile, 'w')

        f.write("S=${WORKDIR}/${P}\n\n")
        f.write('DESCRIPTION="' + self.panelMain.Desc.GetValue() + '"\n\n')
        f.write('HOMEPAGE="' + self.panelMain.Homepage.GetValue() + '"\n\n')
        f.write('SRC_URI="' + self.panelMain.URI.GetValue() + '"\n\n')
        f.write('LICENSE="' + self.panelMain.License + '"\n\n')
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
        c = self.panelCompile.ed.GetText()
        for line in c:
            f.write(line + '\n')
        f.write('\n\n')
        i = self.panelInstall.ed.GetText()
        for line in i:
            f.write(line + '\n')
        f.write('\n\n')

        #CHANGELOG.write(self.panelChangelog.ed.GetText())


class GetURIDialog(wxDialog):

    """ Dialog box that pops up for URI """

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
        self.URI = wxTextCtrl(self, -1, "http://", size=(280,-1))
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
        """Set titlebar and help provider for entire app"""
        title = 'Abeni - The ebuild Builder'
        provider = wxSimpleHelpProvider()
        wxHelpProvider_Set(provider)
        frame=MyFrame(None, -1, title)
        frame.Show(true)
        self.SetTopWindow(frame)
        return true

app=MyApp(0)
app.MainLoop()

