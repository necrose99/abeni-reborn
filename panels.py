from wxPython.wx import *
import urlparse, string
from wxPython.gizmos import *
from wxPython.lib.editor import wxEditor


class main(wxPanel):
    """
    Main panel for entering info
    """

    def __init__(self, parent, sb, pref):
        wxPanel.__init__(self, parent, -1)
        self.pref = pref
        self.parent=parent
        self.sb = sb

        row = 20
        col = 130
        width = 260

        wxStaticText(self, -1, "Package URI", wxPoint(15, row), wxSize(145, 20))
        self.URI = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Package Name", wxPoint(15, row), wxSize(145, 20))
        self.Name = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Package Rev", wxPoint(15, row), wxSize(145, 20))
        self.Rev = wxTextCtrl(self, wxNewId(), "0", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Homepage", wxPoint(15, row), wxSize(145, 20))
        self.Homepage = wxTextCtrl(self, wxNewId(), "http://", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Description", wxPoint(15, row), wxSize(145, 20))
        self.Desc = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "USE variables", wxPoint(15, row), wxSize(145, 20))
        self.USE = wxTextCtrl(self, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Slot", wxPoint(15, row), wxSize(145, 20))
        self.Slot = wxTextCtrl(self, wxNewId(), "0", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "Keywords", wxPoint(15, row), wxSize(145, 20))
        self.Arch = wxTextCtrl(self, wxNewId(), "~x86", wxPoint(col, row), wxSize(width, 20))

        row+=30
        wxStaticText(self, -1, "License", wxPoint(15, row), wxSize(145, 20))
        licenseList = ['Artistic', 'BSD', 'GPL-1', 'GPL-2']
        self.ch = wxChoice(self, wxNewId(), (col, row), choices = licenseList)
        EVT_CHOICE(self, wxNewId(), self.EvtChoice)


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
        self.Name.SetValue(file)


class depends(wxPanel):
    """
    This class is for adding DEPENDS

    """

    def __init__(self, parent, statusbar, pref):
        wxPanel.__init__(self, parent, -1)
        self.statusbar = statusbar
        self.pref = pref
        self.parent=parent
        self.elb1 = wxEditableListBox(self, -1, "DEPENDS",
                                     (10,10), (250, 150),)

        self.elb2 = wxEditableListBox(self, -1, "RDEPENDS",
                                     (290,10), (250, 150),)


class changelog(wxPanel):
    """
    This class is for viewing the Changelog file
    TODO: Use the new simple wxEditor

    """

    def __init__(self, parent, statusbar, pref):
        wxPanel.__init__(self, parent, -1)
        self.statusbar = statusbar
        self.pref = pref
        self.parent=parent
        ed = wxEditor(self, -1, style=wxSUNKEN_BORDER)
        box = wxBoxSizer(wxVERTICAL)
        box.Add(ed, 1, wxALL|wxGROW, 1)
        self.SetSizer(box)
        self.SetAutoLayout(True)

        ed.SetText(open('/usr/portage/skel.ChangeLog').readlines())


class compile(wxPanel):
    """
    This class is for setting the compile specifications
    using a simple text editor

    """

    def __init__(self, parent, statusbar, pref):
        wxPanel.__init__(self, parent, -1)
        self.statusbar = statusbar
        self.pref = pref
        self.parent=parent
        ed = wxEditor(self, -1, style=wxSUNKEN_BORDER)
        box = wxBoxSizer(wxVERTICAL)
        box.Add(ed, 1, wxALL|wxGROW, 1)
        self.SetSizer(box)
        self.SetAutoLayout(True)

        ed.SetText(["src_compile(){",
                    "    ./configure \\",
                    "       --host=${CHOST} \\",
                    "       --prefix=/usr \\",
                    "       --infodir=/usr/share/info \\",
                    "       --mandir=/usr/share/man || die './configure failed'",
                    "    emake || die",
                    "}"

                    ])

class build(wxPanel):
    """
    This class is for setting the build specifications
    using a simple text editor

    """

    def __init__(self, parent, statusbar, pref):
        wxPanel.__init__(self, parent, -1)
        self.statusbar = statusbar
        self.pref = pref
        self.parent=parent
        ed = wxEditor(self, -1, style=wxSUNKEN_BORDER)
        box = wxBoxSizer(wxVERTICAL)
        box.Add(ed, 1, wxALL|wxGROW, 1)
        self.SetSizer(box)
        self.SetAutoLayout(True)

        ed.SetText(["build_src(){",
                        "make DESTDIR=${D} install || die",
                    "}"
                  ])