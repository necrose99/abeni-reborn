#Boa:Frame:GetIUSEDialog

from wxPython.wx import *
from wxPython.gizmos import *

def create(parent):
    return GetIUSEDialog(parent)

[wxID_GETIUSEDIALOG,  
 wxID_GETIUSEDIALOGEDITABLELISTBOX1, wxID_GETIUSEDIALOGPANEL1, 
 wxID_GETIUSEDIALOGSTATICBOX1, 
] = map(lambda _init_ctrls: wxNewId(), range(4))

class GetIUSEDialog(wxDialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, prnt, -1, 
              pos=wxPoint(271, 228), size=wxSize(527, 308),
              title='IUSE')
        self.SetClientSize(wxSize(527, 308))
        self.SetAutoLayout(True)

        self.panel1 = wxPanel(id=wxID_GETIUSEDIALOGPANEL1, name='panel1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(528, 406),
              style=wxTAB_TRAVERSAL)
        self.panel1.SetAutoLayout(True)

        self.editableListBox1 = wxEditableListBox(id=wxID_GETIUSEDIALOGEDITABLELISTBOX1,
              label='See Help menu for list of USE vars', name='editableListBox1', parent=self.panel1,
              pos=wxPoint(40, 40), size=wxSize(432, 184))

        self.staticBox1 = wxStaticBox(id=wxID_GETIUSEDIALOGSTATICBOX1,
              label='IUSE', name='staticBox1', parent=self.panel1,
              pos=wxPoint(8, 8), size=wxSize(512, 290), style=0)

        self.button1 = wxButton(id=wxID_OK, label='Ok',
              name='button1', parent=self.panel1, pos=wxPoint(128, 252),
              size=wxSize(80, 24), style=0)

        self.button2 = wxButton(id=wxID_CANCEL, label='Cancel',
              name='button2', parent=self.panel1, pos=wxPoint(324, 252),
              size=wxSize(80, 24), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)
        l = parent.GetIUSE()
        if not len(l):
            l = ['""']
        self.editableListBox1.SetStrings(l)

