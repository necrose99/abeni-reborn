from wxPython.wx import *
from wxPython.help import *
from options import *
from wxPython.lib.grids import wxGridSizer, wxFlexGridSizer

class GetURIDialog(wxDialog):

    """Dialog box that pops up for URI"""

    def __init__(self, parent, ID, title,
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxDEFAULT_DIALOG_STYLE):
        provider = wxSimpleHelpProvider()
        wxHelpProvider_Set(provider)

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
        label.SetHelpText("Enter the URI for the package or 'CVS' for cvs eclass template.")
        box.Add(label, 0, wxALIGN_CENTRE|wxALL, 5)
        self.URI = wxTextCtrl(self, -1, "http://", size=(280,-1))
        self.URI.SetHelpText("Enter the URI for the package or 'CVS' for cvs eclass template.")
        box.Add(self.URI, 1, wxALIGN_CENTRE|wxALL, 5)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)

        box = wxBoxSizer(wxHORIZONTAL)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        text = wxStaticText(self, -1, "Enter CVS for CVS eclass template.")
        sizer.Add(text, 0, wxALIGN_CENTER|wxALL, 5)
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


class Preferences(wxDialog):

    """Modify preferences"""

    def __init__(self, parent, ID, title,
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxDEFAULT_DIALOG_STYLE):

        pre = wxPreDialog()
        pre.SetExtraStyle(wxDIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.this = pre.this

        myOptions = Options()
        self.pref = myOptions.Prefs()
        btnOK = wxButton(self, wxID_OK, " OK ")
        btnOK.SetDefault()
        btnCancel = wxButton(self, wxID_CANCEL, " Cancel ")
        vs = wxBoxSizer(wxVERTICAL)
        box1_title = wxStaticBox( self, -1, "Preferences")
        box1 = wxStaticBoxSizer( box1_title, wxVERTICAL )
        gs = wxGridSizer(7, 2, 2, 8)  # rows, cols, hgap, vgap
        self.browser = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.browser.SetValue(self.pref['browser'])
        self.xterm = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.xterm.SetValue(self.pref['xterm'])
        self.diff = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.diff.SetValue(self.pref['diff'])
        self.editor = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.editor.SetValue(self.pref['editor'])
        self.autoTabs = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.autoTabs.SetValue(self.pref['autoTabs'])
        self.fileBrowser = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.fileBrowser.SetValue(self.pref['fileBrowser'])

        gs.AddMany([
        (wxStaticText(self, -1, "Web browser"), 0, wxALIGN_LEFT),
        (self.browser, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "xterm"), 0, wxALIGN_LEFT),
        (self.xterm, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "GUI diff program"), 0, wxALIGN_LEFT),
        (self.diff, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "External editor"), 0, wxALIGN_LEFT),
        (self.editor, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "Auto tabs (yes/no)"), 0, wxALIGN_LEFT),
        (self.autoTabs, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "File Browser"), 0, wxALIGN_LEFT),
        (self.fileBrowser, 0, wxALIGN_RIGHT),
        (btnOK, 0, wxALIGN_CENTER),
        (btnCancel, 0, wxALIGN_CENTER)
        ])

        vs.AddSizer(box1, 1, wxALL, 5 )
        box1.AddSizer(gs, 1, wxALL, 5 )
        vs.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(vs)
        self.browser.SetFocus()


