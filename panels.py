from wxPython.wx import *
import urlparse, string
from wxPython.gizmos import *
from wxPython.lib.editor import wxEditor


class main(wxPanel):

    """Main panel for entering info"""

    def __init__(self, parent, sb, pref):
        wxPanel.__init__(self, parent, -1)
        self.pref = pref
        self.parent=parent
        self.sb = sb

        #Custom variable globals
        self.text = []
        self.newVar = []
        self.vrow = 30

        row = 20
        col = 130
        width = 260
        self.group1_ctrls = []

        text1 = wxStaticText(self, -1, "Ebuild")
        self.Ebuild = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text2 = wxStaticText(self, -1, "Ebuild File")
        self.EbuildFile = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30

        self.group2_ctrls = []
        text3 = wxStaticText(self, -1, "SRC_URI")
        self.URI = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text5 = wxStaticText(self, -1, "HOMEPAGE")
        self.Homepage = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        self.Homepage.SetFocus()
        row+=30
        text6 = wxStaticText(self, -1, "DESCRIPTION")
        self.Desc = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text7 = wxStaticText(self, -1, "USE")
        self.USE = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text8 = wxStaticText(self, -1, "SLOT")
        self.Slot = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text9 = wxStaticText(self, -1, "KEYWORDS")
        self.Keywords = wxTextCtrl(self, wxNewId(), "", wxPoint(0,0), wxSize(250, 20))
        row+=30
        text10 = wxStaticText(self, -1, "LICENSE")
        licenseList = ['Artistic', 'BSD', 'GPL-1', 'GPL-2']
        self.group3_ctrls = []

        chEvt = wxNewId()
        self.ch = wxChoice(self, chEvt, wxPoint(0,0), choices = licenseList)
        self.License = licenseList[0]
        EVT_CHOICE(self, chEvt, self.EvtChoice)
        #text11 = wxStaticText(self, -1, "Choose 'New Variable' in the 'Edit' menu to add new variables.")
        #text12 = wxStaticText(self, -1, "     ")

        self.group1_ctrls.append((text1, self.Ebuild))
        self.group1_ctrls.append((text2, self.EbuildFile))

        self.group2_ctrls.append((text3, self.URI))
        #self.group2_ctrls.append((text4, self.Rev))
        self.group2_ctrls.append((text5, self.Homepage))
        self.group2_ctrls.append((text6, self.Desc))
        self.group2_ctrls.append((text7, self.USE))
        self.group2_ctrls.append((text8, self.Slot))
        self.group2_ctrls.append((text9, self.Keywords))
        self.group2_ctrls.append((text10, self.ch))

        #self.group3_ctrls.append((text11, text12))

        # Layout controls on panel:
        vs = wxBoxSizer( wxVERTICAL )
        box1_title = wxStaticBox( self, -1, "Ebuild Info")
        box1 = wxStaticBoxSizer( box1_title, wxVERTICAL )
        grid1 = wxFlexGridSizer( 0, 2, 0, 20 )
        for ctrl, text in self.group1_ctrls:
            grid1.AddWindow( ctrl, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )
            grid1.AddWindow( text, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )

        box1.AddSizer( grid1, 0, wxALIGN_LEFT|wxALL, 5 )
        vs.AddSizer( box1, 1, wxALIGN_LEFT|wxALL, 5 )

        box2_title = wxStaticBox( self, -1, "Default Variables" )
        box2 = wxStaticBoxSizer( box2_title, wxVERTICAL )
        grid2 = wxFlexGridSizer( 0, 2, 0, 0 )
        for ctrl, text in self.group2_ctrls:
            grid2.AddWindow( ctrl, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )
            grid2.AddWindow( text, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )

        box2.AddSizer( grid2, 0, wxALIGN_LEFT|wxALL, 5 )
        vs.AddSizer( box2, 2, wxALIGN_LEFT|wxALL, 5 )

        #vs2 = wxBoxSizer( wxVERTICAL )
        #box3_title = wxStaticBox( self, -1, "Custom Variables" )
        #box3 = wxStaticBoxSizer( box3_title, wxVERTICAL )
        #self.grid3 = wxFlexGridSizer( 0, 1, 0, 0 )
        #for ctrl, text in self.group3_ctrls:
        #    self.grid3.AddWindow( ctrl, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )
        #    self.grid3.AddWindow( text, 0, wxALIGN_LEFT|wxLEFT|wxRIGHT|wxTOP, 5 )

        #box3.AddSizer(self.grid3, 0, wxALIGN_LEFT|wxALL, 5 )
        #vs2.AddSizer(box3, 0, wxALIGN_RIGHT|wxALL, 5 )

        self.SetSizer(vs)
        vs.Fit(self)
        #self.SetSizer(vs2)
        #vs2.Fit(self)
        self.boxt = wxStaticBox( self, -1, "Other Variables", wxPoint(400, 5), wxSize(390, 40))

    def AddVar(self, var):
        t = wxStaticText(self, -1, var, wxPoint(410, self.vrow))
        self.text.append(t)
        v = wxTextCtrl(self, wxNewId(), "", wxPoint(525, self.vrow), wxSize(250, 20))
        v.SetFocus()
        self.newVar.append(v)
        self.vrow += 30
        self.boxt.Destroy()
        h = self.vrow + 20
        self.boxt = wxStaticBox( self, -1, "Other Variables", wxPoint(400, 5), wxSize(390, h))

    def PopulateDefault(self):
        self.Keywords.SetValue("~x86")
        self.Slot.SetValue("0")
        self.Homepage.SetValue("http://")

    def EvtChoice(self, event):
        self.License = event.GetString()

    def SetURI(self, uri):
        self.URI.SetValue(uri)

    def SetName(self, uri):
        path = urlparse.urlparse(uri)[2]
        path = string.split(path, '/')
        file = path[len(path)-1]
        file = string.replace(file, ".tgz", "")
        file = string.replace(file, ".tar.gz", "")
        file = string.replace(file, ".tar.bz2", "")
        file = string.replace(file, ".tbz2", "")
        self.SetEbuildName(file)

    def SetEbuildName(self, file):
        self.ebuildName = file + ".ebuild"

    def GetEbuildName(self):
        return self.ebuildName

    def SetEbuild(self):
        self.EbuildFile.SetValue(self.ebuildName)
        ebuild = string.split(self.ebuildName, '-')
        self.Ebuild.SetValue(ebuild[0])


class depend(wxPanel):

    """This class is for adding DEPEND and RDEPEND info"""

    def __init__(self, parent, statusbar, pref):
        wxPanel.__init__(self, parent, -1)
        self.statusbar = statusbar
        self.pref = pref
        self.parent=parent
        self.elb1 = wxEditableListBox(self, -1, "DEPEND",
                                     (10,10), (250, 150),)

        self.elb2 = wxEditableListBox(self, -1, "RDEPEND",
                                     (290,10), (250, 150),)


class changelog(wxPanel):

    """This class is for viewing the Changelog file"""

    def __init__(self, parent, statusbar, pref):
        wxPanel.__init__(self, parent, -1)
        self.statusbar = statusbar
        self.pref = pref
        self.parent=parent
        self.ed = wxEditor(self, -1, style=wxSUNKEN_BORDER)
        box = wxBoxSizer(wxVERTICAL)
        box.Add(self.ed, 1, wxALL|wxGROW, 1)
        self.SetSizer(box)
        self.SetAutoLayout(True)

        self.ed.SetText(open('/usr/portage/skel.ChangeLog').readlines())


class compile(wxPanel):

    """Set compile specifications using a simple text editor"""

    def __init__(self, parent, statusbar, pref):
        wxPanel.__init__(self, parent, -1)
        self.statusbar = statusbar
        self.pref = pref
        self.parent=parent
        self.ed = wxEditor(self, -1, style=wxSUNKEN_BORDER)
        box = wxBoxSizer(wxVERTICAL)
        box.Add(self.ed, 1, wxALL|wxGROW, 1)
        self.SetSizer(box)
        self.SetAutoLayout(True)

        self.ed.SetText(["src_compile(){",
                    "    ./configure \\",
                    "       --host=${CHOST} \\",
                    "       --prefix=/usr \\",
                    "       --infodir=/usr/share/info \\",
                    "       --mandir=/usr/share/man || die './configure failed'",
                    "    emake || die",
                    "}"

                    ])

class install(wxPanel):

    """Set the install specifications using a simple text editor"""

    def __init__(self, parent, statusbar, pref):
        wxPanel.__init__(self, parent, -1)
        self.statusbar = statusbar
        self.pref = pref
        self.parent=parent
        self.ed = wxEditor(self, -1, style=wxSUNKEN_BORDER)
        box = wxBoxSizer(wxVERTICAL)
        box.Add(self.ed, 1, wxALL|wxGROW, 1)
        self.SetSizer(box)
        self.SetAutoLayout(True)

        self.ed.SetText(["src_install(){",
                        "make DESTDIR=${D} install || die",
                    "}"
                  ])