from wxPython.wx import *
from wxPython.lib.buttons import *

from options import *

def create(parent):
    return DevPrefs(parent)

[wxID_DEVPREFS, wxID_DEVPREFSBUTTON2, wxID_DEVPREFSCVSOPTIONS,
 wxID_DEVPREFSCVSROOT, wxID_DEVPREFSGENBUTTON1, wxID_DEVPREFSSTATICBOX1,
 wxID_DEVPREFSSTATICTEXT1, wxID_DEVPREFSSTATICTEXT2, wxID_DEVPREFSSTATICTEXT3,
 wxID_DEVPREFSSTATICTEXT5, wxID_DEVPREFSUSERNAME,
] = map(lambda _init_ctrls: wxNewId(), range(11))

class DevPrefs(wxDialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_DEVPREFS, name='DevPrefs', parent=prnt,
              pos=wxPoint(296, 275), size=wxSize(464, 252),
              style=wxDEFAULT_DIALOG_STYLE, title='Developer Preferences')
        self.SetClientSize(wxSize(464, 252))

        self.userName = wxTextCtrl(id=wxID_DEVPREFSUSERNAME, name='userName',
              parent=self, pos=wxPoint(272, 64), size=wxSize(168, 24), style=0,
              value='')

        self.staticText1 = wxStaticText(id=wxID_DEVPREFSSTATICTEXT1,
              label='User name to run /usr/bin/cvs as', name='staticText1',
              parent=self, pos=wxPoint(25, 66), size=wxSize(190, 16), style=0)

        self.staticBox1 = wxStaticBox(id=wxID_DEVPREFSSTATICBOX1,
              label='Gentoo Developer Preferences', name='staticBox1',
              parent=self, pos=wxPoint(8, 0), size=wxSize(448, 192), style=0)

        self.staticText5 = wxStaticText(id=wxID_DEVPREFSSTATICTEXT5,
              label='(For official Gentoo Devlopers - not users)',
              name='staticText5', parent=self, pos=wxPoint(20, 24),
              size=wxSize(260, 17), style=0)
        self.staticText5.SetForegroundColour(wxColour(255, 0, 0))

        self.staticText2 = wxStaticText(id=wxID_DEVPREFSSTATICTEXT2,
              label='Options for cvs (-z3 etc)', name='staticText2',
              parent=self, pos=wxPoint(24, 104), size=wxSize(141, 16), style=0)

        self.cvsOptions = wxTextCtrl(id=wxID_DEVPREFSCVSOPTIONS,
              name='cvsOptions', parent=self, pos=wxPoint(272, 104),
              size=wxSize(168, 24), style=0, value='')

        self.button2 = wxButton(id=wxID_OK, label='OK', name='button2',
              parent=self, pos=wxPoint(84, 208), size=wxSize(80, 26), style=0)

        self.cvsRoot = wxTextCtrl(id=wxID_DEVPREFSCVSROOT, name='cvsRoot',
              parent=self, pos=wxPoint(272, 144), size=wxSize(168, 24), style=0,
              value='')

        self.staticText3 = wxStaticText(id=wxID_DEVPREFSSTATICTEXT3,
              label='CVS root', name='staticText3', parent=self, pos=wxPoint(24,
              149), size=wxSize(61, 16), style=0)

        self.genButton1 = wxGenButton(ID=wxID_CANCEL, label='Cancel',
              name='genButton1', parent=self, pos=wxPoint(304, 208),
              size=wxSize(81, 28), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)
        myOptions = Options()
        pref = myOptions.Prefs()
        self.cvsRoot.SetValue(pref['cvsRoot'])
        self.cvsOptions.SetValue(pref['cvsOptions'])
        self.userName.SetValue(pref['userName'])

