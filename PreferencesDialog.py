
from wxPython.wx import *
from wxPython.help import *

from options import *

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
        gs = wxGridSizer(9, 2, 2, 8)  # rows, cols, hgap, vgap
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
        self.statuslist = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.statuslist.SetValue(self.pref['statuslist'])
        self.use = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.use.SetValue(self.pref['use'])
        self.features = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.features.SetValue(self.pref['features'])
        self.log = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.log.SetValue(self.pref['log'])
        self.email = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.email.SetValue(self.pref['email'])

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
        (wxStaticText(self, -1, "Abeni status modes"), 0, wxALIGN_LEFT),
        (self.statuslist, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "USE"), 0, wxALIGN_LEFT),
        (self.use, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "FEATURES"), 0, wxALIGN_LEFT),
        (self.features, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "Log (bottom/window)"), 0, wxALIGN_LEFT),
        (self.log, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "Bugzilla Email Addr"), 0, wxALIGN_LEFT),
        (self.email, 0, wxALIGN_RIGHT),

        (btnOK, 0, wxALIGN_CENTER),
        (btnCancel, 0, wxALIGN_CENTER)
        ])

        vs.AddSizer(box1, 1, wxALL, 5 )
        box1.AddSizer(gs, 1, wxALL, 5 )
        vs.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(vs)
        self.browser.SetFocus()
