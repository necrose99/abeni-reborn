#Boa:Frame:GetIUSEDialog

import wx
#from wxPython.gizmos import *

#TODO: Create this dialog using wxglade

def create(parent):
    return GetIUSEDialog(parent)

[wxID_GETIUSEDIALOG,  
 wxID_GETIUSEDIALOGEDITABLELISTBOX1, wxID_GETIUSEDIALOGPANEL1, 
 wxID_GETIUSEDIALOGSTATICBOX1, 
] = map(lambda _init_ctrls: wx.NewId(), range(4))

class GetIUSEDialog(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, prnt, -1, 
              pos=wx.Point(271, 228), size=wx.Size(527, 308),
              title='IUSE')
        self.SetClientSize(wx.Size(527, 308))
        self.SetAutoLayout(True)

        self.panel1 = wx.Panel(id=wxID_GETIUSEDIALOGPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(528, 406),
              style=wx.TAB_TRAVERSAL)
        self.panel1.SetAutoLayout(True)

        self.editableListBox1 = wx.EditableListBox(id=wxID_GETIUSEDIALOGEDITABLELISTBOX1,
              label='See Help menu for list of USE vars', name='editableListBox1', parent=self.panel1,
              pos=wx.Point(40, 40), size=wx.Size(432, 184))

        self.staticBox1 = wx.StaticBox(id=wxID_GETIUSEDIALOGSTATICBOX1,
              label='IUSE', name='staticBox1', parent=self.panel1,
              pos=wx.Point(8, 8), size=wx.Size(512, 290), style=0)

        self.button1 = wx.Button(id=wx.ID_OK, label='Ok',
              name='button1', parent=self.panel1, pos=wx.Point(128, 252),
              size=wx.Size(80, 24), style=0)

        self.button2 = wx.Button(id=wx.ID_CANCEL, label='Cancel',
              name='button2', parent=self.panel1, pos=wx.Point(324, 252),
              size=wx.Size(80, 24), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)
        l = parent.GetIUSE()
        if not len(l):
            l = ['""']
        self.editableListBox1.SetStrings(l)

