from wxPython.wx import *
from wxPython.help import *

import utils

class EmergeDialog(wxDialog):

    """Dialog box for running emerge with options"""

    def __init__(self, parent, ID, title,
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxDEFAULT_DIALOG_STYLE):
        provider = wxSimpleHelpProvider()
        wxHelpProvider_Set(provider)
        self.parent = parent
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

        useLabel = wxStaticText(self, -1, "USE=")
        useLabel.SetHelpText("Enter any USE variables for the emerge command.")
        box.Add(useLabel, 0, wxALIGN_CENTRE|wxALL, 5)

        self.use = wxTextCtrl(self, -1, parent.pref["use"], size=(100,-1))
        self.use.SetHelpText("Enter any USE variables for the emerge command.")
        box.Add(self.use, 1, wxALIGN_CENTRE|wxALL, 5)

        featuresLabel = wxStaticText(self, -1, "FEATURES=")
        featuresLabel.SetHelpText("Enter any variables for FEATURES.")
        box.Add(featuresLabel, 0, wxALIGN_CENTRE|wxALL, 5)

        self.features = wxTextCtrl(self, -1, parent.pref["features"], size=(100,-1))
        self.features.SetHelpText("Enter any variables for FEATURES.")
        box.Add(self.features, 1, wxALIGN_CENTRE|wxALL, 5)

        kwLabel = wxStaticText(self, -1, "ACCEPT_KEYWORDS=")
        kwLabel.SetHelpText("Enter archs (x86, ~x86 etc)")
        box.Add(kwLabel, 0, wxALIGN_CENTRE|wxALL, 5)

        self.kw = wxTextCtrl(self, -1, "", size=(100,-1))
        self.kw.SetHelpText("Enter arch")
        box.Add(self.kw, 1, wxALIGN_CENTRE|wxALL, 5)

        sizer.Add(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        box = wxBoxSizer(wxHORIZONTAL)

        self.cat_pack_ver = utils.GetCatPackVer(parent)

        cmd = "emerge --nospinner =%s"  % self.cat_pack_ver

        pretend_cmd = "emerge --nospinner -pv =%s"  % self.cat_pack_ver

        self.kw.SetValue(utils.GetArch())
        self.emerge = wxTextCtrl(self, -1, cmd, size=(560,-1))
        self.emerge.SetHelpText("Enter any options for the emerge command.")
        box.Add(self.emerge, 1, wxALIGN_CENTRE|wxALL, 5)
        sizer.Add(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        box = wxBoxSizer(wxHORIZONTAL)
        sizer.Add(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        sizer.Add(line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxRIGHT|wxTOP, 5)
        box = wxBoxSizer(wxHORIZONTAL)

        btn = wxButton(self, wxID_OK, " Emerge ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        wxID_PRETEND_EMERGE = wxNewId()
        btn = wxButton(self, wxID_PRETEND_EMERGE, " Pretend ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        EVT_BUTTON(btn, wxID_PRETEND_EMERGE, self.OnPretendButton)


        btn = wxButton(self, wxID_CANCEL, " Cancel ")
        btn.SetDefault()
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        btn = wxContextHelpButton(self)
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        sizer.Add(box, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def OnPretendButton(self, event):
        """ emerge -pv this ebuild """
        pretend_cmd = "ACCEPT_KEYWORDS='%s' FEATURES='%s' USE='%s' emerge --nospinner -pv =%s" \
                   % (self.kw.GetValue(), self.features.GetValue(), self.use.GetValue(), self.cat_pack_ver)
        utils.write(self.parent, ">>> %s" % pretend_cmd)
        utils.ExecuteInLog(self.parent, pretend_cmd)
