import os

from wxPython.wx import *

#---------------------------------------------------------------------------



[wxID_METADATADIALOG, wxID_METADATADIALOGGENBUTTON1,
 wxID_METADATADIALOGGENBUTTON2, wxID_METADATADIALOGNOTEBOOK1,
 wxID_METADATADIALOGPANEL1, wxID_METADATADIALOGSTYLEDTEXTCTRL1,
 wxID_METADATADIALOGSTYLEDTEXTCTRL2,
] = map(lambda _init_ctrls: wxNewId(), range(7))

class MetadataDialog(wxDialog):
    def _init_coll_notebook1_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.styledTextCtrl1, select=True,
                       text='metadata.xml')
        parent.AddPage(imageId=-1, page=self.styledTextCtrl2, select=False,
                       text='skel.metadata.xml')

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_METADATADIALOG, name='MetadataDialog',
              parent=prnt, pos=wxPoint(254, 137), size=wxSize(683, 445),
              style=wxDEFAULT_DIALOG_STYLE, title='Metadata')
        self.SetClientSize(wxSize(683, 445))

        self.panel1 = wxPanel(id=wxID_METADATADIALOGPANEL1, name='panel1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(683, 445),
              style=wxTAB_TRAVERSAL)

        self.notebook1 = wxNotebook(id=wxID_METADATADIALOGNOTEBOOK1,
              name='notebook1', parent=self.panel1, pos=wxPoint(8, 24),
              size=wxSize(664, 352), style=0)

        self.genButton1 = wxGenButton(ID=wxID_OK, label='OK',
              name='genButton1', parent=self.panel1, pos=wxPoint(112, 400),
              size=wxSize(81, 28), style=0)

        self.genButton2 = wxGenButton(ID=wxID_CANCEL, label='Cancel', name='genButton2',
              parent=self.panel1, pos=wxPoint(456, 408), size=wxSize(81, 28),
              style=0)

        self.styledTextCtrl1 = wxStyledTextCtrl(id=wxID_METADATADIALOGSTYLEDTEXTCTRL1,
              name='styledTextCtrl1', parent=self.notebook1, pos=wxPoint(0, 0),
              size=wxSize(660, 318), style=0)

        self.styledTextCtrl2 = wxStyledTextCtrl(id=wxID_METADATADIALOGSTYLEDTEXTCTRL2,
              name='styledTextCtrl2', parent=self.notebook1, pos=wxPoint(0, 0),
              size=wxSize(660, 318), style=0)

        self._init_coll_notebook1_Pages(self.notebook1)

    def __init__(self, parent):
        self._init_ctrls(parent)
        metadata = "%s/metadata.xml" % os.path.dirname(parent.filename)
        if os.path.exists(metadata):
            self.styledTextCtrl1.SetText(open(metadata).read())

        #TODO: get PORTDIR
        skel = open("/usr/portage/skel.metadata.xml").read()
        self.styledTextCtrl2.EmptyUndoBuffer()
        #self.styledTextCtrl2.Colourise(0, -1)
        #self.styledTextCtrl2.SetMarginType(1, wxSTC_MARGIN_NUMBER)
        #self.styledTextCtrl2.SetMarginWidth(1, 25)
        self.styledTextCtrl2.SetLexer(wxSTC_LEX_XML)
        self.styledTextCtrl2.SetText(skel)
