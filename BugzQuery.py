from wxPython.wx import *

[wxID_BUGZQUERY, wxID_BUGZQUERYBUGNBRBUTTON, wxID_BUGZQUERYBUGNBRSTATICBOX,
 wxIDCANCEL, wxID_BUGZQUERYQUERYBUTTON,
 wxID_BUGZQUERYQUERYSTATICBOX, wxID_BUGZQUERYQUERYSTATICTEXT,
 wxID_BUGZQUERYQUERYTEXTCTRL, wxID_BUGZQUERYTEXTCTRL1,
] = map(lambda _init_ctrls: wxNewId(), range(9))

class BugzQuery(wxDialog):

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_BUGZQUERY, name='BugzQuery',
              parent=prnt, pos=wxPoint(254, 170), size=wxSize(330, 284),
              style=wxDEFAULT_DIALOG_STYLE, title='Bugzilla Query')
        self.SetClientSize(wxSize(330, 284))

        self.BugNbrbutton = wxButton(id=wxID_BUGZQUERYBUGNBRBUTTON,
              label='Fetch', name='BugNbrbutton', parent=self, pos=wxPoint(112,
              48), size=wxSize(120, 22), style=0)
        self.BugNbrbutton.SetToolTipString('')
        EVT_BUTTON(self.BugNbrbutton, wxID_BUGZQUERYBUGNBRBUTTON,
              self.OnBugnbrbuttonButton)

        self.BugNbrstaticBox = wxStaticBox(id=wxID_BUGZQUERYBUGNBRSTATICBOX,
              label='Search by Bug Nbr', name='BugNbrstaticBox', parent=self,
              pos=wxPoint(8, 8), size=wxSize(312, 96), style=0)

        self.textCtrl1 = wxTextCtrl(id=wxID_BUGZQUERYTEXTCTRL1,
              name='textCtrl1', parent=self, pos=wxPoint(16, 48),
              size=wxSize(80, 22), style=0, value='')

        self.QuerystaticBox = wxStaticBox(id=wxID_BUGZQUERYQUERYSTATICBOX,
              label='Query by Search Term', name='QuerystaticBox', parent=self,
              pos=wxPoint(8, 120), size=wxSize(312, 152), style=0)

        self.QuerystaticText = wxStaticText(id=wxID_BUGZQUERYQUERYSTATICTEXT,
              label='Enter search criteria (contains all strings)',
              name='QuerystaticText', parent=self, pos=wxPoint(24, 154),
              size=wxSize(229, 16), style=0)

        self.QuerytextCtrl = wxTextCtrl(id=wxID_BUGZQUERYQUERYTEXTCTRL,
              name='QuerytextCtrl', parent=self, pos=wxPoint(24, 184),
              size=wxSize(280, 22), style=0, value='')

        self.Querybutton = wxButton(id=wxID_BUGZQUERYQUERYBUTTON,
              label='Search', name='Querybutton', parent=self, pos=wxPoint(40,
              232), size=wxSize(112, 22), style=0)
        EVT_BUTTON(self.Querybutton, wxID_BUGZQUERYQUERYBUTTON,
              self.OnQuerybuttonButton)

        self.CancelButton = wxButton(id=wxID_CANCEL,
              label='Cancel', name='CancelButton', parent=self, pos=wxPoint(184,
              232), size=wxSize(104, 22), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def MyMessage(self, msg, title, type="info"):
        """Simple informational dialog"""
        if type == "info":
            icon = wxICON_INFORMATION
        elif type == "error":
            icon = wxICON_ERROR

        dlg = wxMessageDialog(self, msg, title, wxOK | icon)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBugnbrbuttonButton(self, event):
        """Launches browser and searches bugzilla"""
        myOptions = Options()
        pref = myOptions.Prefs()
        bugNbr = self.textCtrl1.GetValue()
        if not bugNbr.isdigit():
            self.MyMessage("Enter a number", "Error", "error")
            return
        URL = "http://bugs.gentoo.org/show_bug.cgi?id=%s" % bugNbr
        if pref['browser']:
            os.system("%s %s &" % (pref['browser'], URL))
        else:
            self.MyMessage("You need to define a browser in preferences.", "Error", "error")

    def OnQuerybuttonButton(self, event):
        """Launches browser and searches bugzilla for string(s)"""
        import urllib
        myOptions = Options()
        pref = myOptions.Prefs()
        t = self.QuerytextCtrl.GetValue()
        t = urllib.quote_plus(t)
        URL = "'http://bugs.gentoo.org/buglist.cgi?query_format=&short_desc_type=allwordssubstr&short_desc=%s'" % t
        if pref['browser']:
            os.system("%s %s &" % (pref['browser'], URL))
        else:
            self.MyMessage("You need to define a browser in preferences.", "Error", "error")
