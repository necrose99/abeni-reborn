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

        row = 20
        col = 130
        width = 260

        wxStaticText(self, -1, "Ebuild", wxPoint(15, row), wxSize(145, 20))
        self.Ebuild = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Ebuild file", wxPoint(15, row), wxSize(145, 20))
        self.EbuildFile = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Package URI", wxPoint(15, row), wxSize(145, 20))
        self.URI = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Ebuild Rev", wxPoint(15, row), wxSize(145, 20))
        self.Rev = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Homepage", wxPoint(15, row), wxSize(145, 20))
        self.Homepage = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))
        self.Homepage.SetFocus()

        row+=30
        wxStaticText(self, -1, "Description", wxPoint(15, row), wxSize(145, 20))
        self.Desc = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "USE variables", wxPoint(15, row), wxSize(145, 20))
        self.USE = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Slot", wxPoint(15, row), wxSize(145, 20))
        self.Slot = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Keywords", wxPoint(15, row), wxSize(145, 20))
        self.Keywords = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "License", wxPoint(15, row), wxSize(145, 20))
        licenseList = ['Artistic', 'BSD', 'GPL-1', 'GPL-2']
        chEvt = wxNewId()
        self.ch = wxChoice(self, chEvt, (col, row), choices = licenseList)
        self.License = licenseList[0]
        EVT_CHOICE(self, chEvt, self.EvtChoice)

    def PopulateDefault(self):
        self.Keywords.SetValue("~x86")
        self.Slot.SetValue("0")
        self.Homepage.SetValue("http://")
        self.Rev.SetValue("0")

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