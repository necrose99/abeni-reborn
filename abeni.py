#!/usr/bin/env python

__author__ = 'Rob Cakebread'
__version__ = '0.0.5'

from wxPython.wx import *
import os, os.path, string, shutil, time, sys
import panels

#Find directory Abeni was started from
appdir = os.path.abspath(os.path.join(os.getcwd(), sys.path[0]))

# Allow gif, jpg, bmp, png handling for wxHtml
wxInitAllImageHandlers()


class MyFrame(wxFrame):
    def __init__(self, parent, id, title):
        wxFrame.__init__(self, parent, -1, title,size=wxSize(600,480))
        self.SetAutoLayout(true)

        # Are we in the process of creating an ebuild?
        self.editing = 0

        # Get options from abenirc file
        self.GetOptions()

        iconFile = ('%s/Images/mocha.png' % appdir)
        icon = wxIcon(iconFile, wxBITMAP_TYPE_PNG)
        self.SetIcon(icon)

        """ Setup wxNotebook in main frame """


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

        """ Create menus, setup keyboard accelerators """
        # File
        menu_file = wxMenu()

        mnuNewID=wxNewId()
        menu_file.Append(mnuNewID, "N&ew")

        mnuNewFromID=wxNewId()
        menu_file.Append(mnuNewFromID, "New F&rom Existing ebuild")

        mnuExitID=wxNewId()
        menu_file.Append(mnuExitID, "E&xit")

        menubar = wxMenuBar()
        menubar.Append(menu_file, "&File")

        # Options
        menu_options = wxMenu()
        mnuPrefID = wxNewId()
        menu_options.Append(mnuPrefID, "Global Preferences")
        menubar.Append(menu_options, "&Options")
        # Help
        menu_help = wxMenu()
        mnuHelpID = wxNewId()
        mnuAboutID = wxNewId()
        menu_help.Append(mnuHelpID,"Contents")
        menu_help.Append(mnuAboutID,"About")
        menubar.Append(menu_help,"&Help")
        self.SetMenuBar(menubar)
        EVT_MENU(self, mnuExitID, self.OnMnuExit)
        EVT_MENU(self, mnuNewID, self.OnMnuNew)
        EVT_MENU(self, mnuNewFromID, self.OnMnuNewFrom)
        EVT_MENU(self, mnuPrefID, self.OnMnuPref)
        EVT_MENU(self, mnuAboutID, self.OnMnuAbout)
        EVT_MENU(self, mnuHelpID, self.OnMnuHelp)

        # Keyboard accelerators
        # TODO: Add for accelerator for each item in menu

        # Alt-X to exit
        aTable = wxAcceleratorTable([(wxACCEL_ALT,  ord('X'), mnuExitID)])
        self.SetAcceleratorTable(aTable)


        """ Create Toolbar with icons """
        newID = wxNewId()
        closeID = wxNewId()
        helpID = wxNewId()
        self.tb = self.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
        newBmp = ('%s/Images/new.bmp' % appdir)
        closeBmp = ('%s/Images/close.bmp' % appdir)
        helpBmp = ('%s/Images/help.bmp' % appdir)
        self.tb.AddSimpleTool(newID, wxBitmap(newBmp, wxBITMAP_TYPE_BMP ) , "Create new ebuild", "Create New ebuild")
        self.tb.AddSimpleTool(closeID, wxBitmap(closeBmp, wxBITMAP_TYPE_BMP ) , "Close ebuild", "Close ebuild")
        self.tb.AddSimpleTool(helpID, wxBitmap(helpBmp, wxBITMAP_TYPE_BMP ) , "Help", "Abeni Help")
        self.tb.Realize()
        EVT_TOOL(self, newID, self.OnMnuNew)
        EVT_TOOL_ENTER(self, -1, self.OnToolZone)
        EVT_TIMER(self, -1, self.OnClearSB)
        self.timer = None



    def GetOptions(self):
        """ Global options from apprc file """
        import options
        myOptions = options.Options()
        self.pref = myOptions.Prefs()
        self.debug = self.pref['debug']


    def OnToolZone(self, event):
        """ Clear statusbar 3 seconds after mouse moves over toolbar icon """
        if self.timer is None:
            self.timer = wxTimer(self)
        if self.timer.IsRunning():
            self.timer.Stop()
        self.timer.Start(3000)
        event.Skip()

    def OnClearSB(self, event):  # called for the timer event handler OnToolZone
        self.SetStatusText("") # Clear status bar after hovering over toolbar icon
        self.timer.Stop()
        self.timer = None

    def OnPageChanged(self, event):
        event.Skip()
        self.nbPage = event.GetSelection()
        #self.tb.Hide()
        #print self.nb.GetPageText(self.nbPage)

    def OnMnuHelp(self, event):
        import Help
        if appdir == ".":
            helpdir = "index.html"
        else:
            #helpdir = ('%s/Docs/index.html' % appdir)
            helpdir = 'index.html'
        Help.showHelp(self, Help.BoaHelpFrame, '%s' % helpdir) #abeni-n.n/Docs/index.html


    def OnMnuNew(self,event):
        if not self.editing:
            win = GetURIDialog(self, -1, "Enter Package URI", size=wxSize(350, 200),
                     style = wxDEFAULT_DIALOG_STYLE
                     )
            win.CenterOnScreen()
            val = win.ShowModal()
            self.URI = win.URI.GetValue()
            if val == wxID_OK:
                self.panelMain=panels.main(self.nb, self.sb, self.pref)
                self.panelDepends=panels.depends(self.nb, self.sb, self.pref)
                self.panelCompile=panels.compile(self.nb, self.sb, self.pref)
                self.panelBuild=panels.build(self.nb, self.sb, self.pref)
                self.panelChangelog=panels.changelog(self.nb, self.sb, self.pref)
                self.panelDepends=panels.depends(self.nb, self.sb, self.pref)

                self.nb.AddPage(self.panelMain, "Main")
                self.panelMain.SetURI(self.URI)
                self.panelMain.SetName(self.URI)

                self.nb.AddPage(self.panelDepends, "Dependencies")
                self.nb.AddPage(self.panelCompile, "Compile")
                self.nb.AddPage(self.panelBuild, "Build")
                self.nb.AddPage(self.panelChangelog, "Changelog")
                self.editing = 1


    def OnMnuNewFrom(self,event):
        pass


    def OnMnuExit(self,event):
        self.Close()

    def OnMnuPref(self, event):
        import OptionFrame
        a = OptionFrame.optionFrame(None, -1, "Global Preferences")
        a.Show(true)

    def OnMnuAbout(self,event):
        dlg = wxMessageDialog(self, 'Abeni is a Python and wxPython application\n by Rob Cakebread released under the GPL license.\n\n',
                              'About Abeni', wxOK | wxICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

from wxPython.help import *
#---------------------------------------------------------------------------
# Create and set a help provider.  Normally you would do this in
# the app's OnInit as it must be done before any SetHelpText calls.
provider = wxSimpleHelpProvider()
wxHelpProvider_Set(provider)
#---------------------------------------------------------------------------

class GetURIDialog(wxDialog):
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

        self.URI = wxTextCtrl(self, -1, "", size=(280,-1))
        self.URI.SetHelpText("Enter the URI for the package. This can be a URL like 'http://...' or a path to a file.")
        box.Add(self.URI, 1, wxALIGN_CENTRE|wxALL, 5)

        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)

        box = wxBoxSizer(wxHORIZONTAL)

        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)

        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        sizer.Add(line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxRIGHT|wxTOP, 5)

        box = wxBoxSizer(wxHORIZONTAL)

        btn = wxContextHelpButton(self)
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        btn = wxButton(self, wxID_OK, " OK ")
        btn.SetDefault()
        #btn.SetHelpText("The OK button completes the dialog")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        btn = wxButton(self, wxID_CANCEL, " Cancel ")
        #btn.SetHelpText("The Cancel button cnacels the dialog. (Duh!)")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        sizer.AddSizer(box, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)



class MyApp(wxApp):
    def OnInit(self):
        title = 'Abeni - The ebuild Builder'
        frame=MyFrame(None, -1, title)
        frame.Show(true)
        self.SetTopWindow(frame)
        return true

app=MyApp(0)
app.MainLoop()
