#Boa:Dialog:wxDialog1

from wxPython.wx import *

def create(parent):
    return wxDialog1(parent)
#[wxID_WXDIALOG1, wxID_OK, wxID_CANCEL,
[wxID_WXDIALOG1,
 wxID_WXDIALOG1PANEL1, wxID_WXDIALOG1RADIOBUTTON1, wxID_WXDIALOG1RADIOBUTTON2,
 wxID_WXDIALOG1RADIOBUTTON3, wxID_WXDIALOG1RADIOBUTTON4,
 wxID_WXDIALOG1RADIOBUTTON5, wxID_WXDIALOG1STATICLINE1,
 wxID_WXDIALOG1STATICLINE2, wxID_WXDIALOG1STATICTEXT1,
 wxID_WXDIALOG1TEXTCTRL1,
] = map(lambda _init_ctrls: wxNewId(), range(11))

class wxDialog1(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_WXDIALOG1, name='', parent=prnt,
              pos=wxPoint(373, 191), size=wxSize(327, 307),
              style=wxDEFAULT_DIALOG_STYLE, title='New Function')
        self._init_utils()
        self.SetClientSize(wxSize(327, 307))

        self.panel1 = wxPanel(id=wxID_WXDIALOG1PANEL1, name='panel1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(327, 307),
              style=wxTAB_TRAVERSAL)

        self.staticText1 = wxStaticText(id=wxID_WXDIALOG1STATICTEXT1,
              label='Function Name', name='staticText1', parent=self.panel1,
              pos=wxPoint(16, 26), size=wxSize(96, 16), style=0)

        self.textCtrl1 = wxTextCtrl(id=wxID_WXDIALOG1TEXTCTRL1,
              name='textCtrl1', parent=self.panel1, pos=wxPoint(112, 24),
              size=wxSize(176, 22), style=0, value='()')

        self.radioButton1 = wxRadioButton(id=wxID_WXDIALOG1RADIOBUTTON1,
              label='empty', name='radioButton1', parent=self.panel1,
              pos=wxPoint(32, 82), size=wxSize(94, 24), style=0)
        self.radioButton1.SetValue(True)
        EVT_RADIOBUTTON(self.radioButton1, wxID_WXDIALOG1RADIOBUTTON1,
              self.OnRadiobutton1Radiobutton)

        self.radioButton2 = wxRadioButton(id=wxID_WXDIALOG1RADIOBUTTON2,
              label='src_compile - empty', name='radioButton2',
              parent=self.panel1, pos=wxPoint(32, 104), size=wxSize(256, 32),
              style=0)
        self.radioButton2.SetValue(False)
        EVT_RADIOBUTTON(self.radioButton2, wxID_WXDIALOG1RADIOBUTTON2,
              self.OnRadiobutton2Radiobutton)

        self.radioButton3 = wxRadioButton(id=wxID_WXDIALOG1RADIOBUTTON3,
              label='src_compile - ./configure - make', name='radioButton3',
              parent=self.panel1, pos=wxPoint(32, 132), size=wxSize(256, 24),
              style=0)
        self.radioButton3.SetValue(False)
        EVT_RADIOBUTTON(self.radioButton3, wxID_WXDIALOG1RADIOBUTTON3,
              self.OnRadiobutton3Radiobutton)

        self.radioButton4 = wxRadioButton(id=wxID_WXDIALOG1RADIOBUTTON4,
              label='src_install - make install', name='radioButton4',
              parent=self.panel1, pos=wxPoint(32, 158), size=wxSize(264, 24),
              style=0)
        self.radioButton4.SetValue(False)
        EVT_RADIOBUTTON(self.radioButton4, wxID_WXDIALOG1RADIOBUTTON4,
              self.OnRadiobutton4Radiobutton)

        self.radioButton5 = wxRadioButton(id=wxID_WXDIALOG1RADIOBUTTON5,
              label='src_install - python setup.py install',
              name='radioButton5', parent=self.panel1, pos=wxPoint(32, 184),
              size=wxSize(264, 24), style=0)
        self.radioButton5.SetValue(False)
        EVT_RADIOBUTTON(self.radioButton5, wxID_WXDIALOG1RADIOBUTTON5,
              self.OnRadiobutton5Radiobutton)

        self.staticLine1 = wxStaticLine(id=wxID_WXDIALOG1STATICLINE1,
              name='staticLine1', parent=self.panel1, pos=wxPoint(8, 56),
              size=wxSize(312, 20), style=0)

        self.staticLine2 = wxStaticLine(id=wxID_WXDIALOG1STATICLINE2,
              name='staticLine2', parent=self.panel1, pos=wxPoint(8, 224),
              size=wxSize(312, 4), style=0)

        self.button1 = wxButton(id=wxID_OK, label='OK',
              name='button1', parent=self.panel1, pos=wxPoint(48, 256),
              size=wxSize(80, 22), style=0)
        self.button1.SetDefault()

        self.button2 = wxButton(id=wxID_CANCEL, label='Cancel',
              name='button2', parent=self.panel1, pos=wxPoint(184, 256),
              size=wxSize(80, 22), style=0)

    def __init__(self, parent):
        """Populate panel with controls"""
        self._init_ctrls(parent)
        self.val = None
        self.textCtrl1.SetFocus()

    def GetFunc(self):
        """Returns function name and function body"""
        self.func = self.textCtrl1.GetValue()
        if self.val == None:
            self.val = self.func + ' {\n\n}\n'
        return self.func, self.val

    def OnRadiobutton1Radiobutton(self, event):
        """empty custom function"""
        self.textCtrl1.SetValue('()')
        self.textCtrl1.SetFocus()

    def OnRadiobutton2Radiobutton(self, event):
        """src_compile - empty"""
        name = 'src_compile()'
        self.textCtrl1.SetValue(name)
        self.val = None

    def OnRadiobutton3Radiobutton(self, event):
        """src_compile - configure/make"""
        name = 'src_compile()'
        self.textCtrl1.SetValue(name)
        self.val = name + ' {\n\teconf || die\n\temake || die\n}\n'

    def OnRadiobutton4Radiobutton(self, event):
        """src_install - make install"""
        name = 'src_install()'
        self.textCtrl1.SetValue(name)
        self.val = name + ' {\n\teinstall || die\n}\n'

    def OnRadiobutton5Radiobutton(self, event):
        """src_install - python setup.py install"""
        name = 'src_install()'
        self.textCtrl1.SetValue(name)
        self.val = name + ' {\n\tpython setup.py install || die\n}\n'
