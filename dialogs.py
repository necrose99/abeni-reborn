from wxPython.wx import *
from wxPython.help import *
from options import *
from wxPython.lib.grids import wxGridSizer, wxFlexGridSizer
from wxPython.lib.buttons import *
import os, gadfly

[wxID_BUGZILLA, wxID_BUGZILLABUGNBR, wxID_BUGZILLABUGNBRSTATICTEXT,
 wxID_BUGZILLABUZILLASTATICBOX, wxID_BUGZILLACANCEL,
 wxID_BUGZILLANOTESSTATICBOX, wxID_BUGZILLANOTESTEXTCTRL, wxID_BUGZILLAOK,
 wxID_BUGZILLARESOLUTIONCOMBO, wxID_BUGZILLASEARCHBUTTON,
 wxID_BUGZILLASTATUSCOMBO,
] = map(lambda _init_ctrls: wxNewId(), range(11))


class BugzillaDialog(wxDialog):
    def __init__(self, parent):
        self._init_ctrls(parent)
        loc = "/home/rob/.abeni/bugz"
        if not os.path.exists("%s/EBUILDS.grl" % loc):
            self.parent.write("Creating project database and tables...")
            self.createDB()
            self.parent.write("Database created.")
        else:
            self.connection = gadfly.gadfly("bugzDB", "/home/rob/.abeni/bugz")
            self.cursor = self.connection.cursor()
        self.LoadInfo()

    def createDB(self):
        self.connection = gadfly.gadfly()
        self.connection.startup("bugzDB", "/home/rob/.abeni/bugz")
        self.cursor = self.connection.cursor()
        cmd = "create table ebuilds (\
           p VARCHAR, \
           package VARCHAR, \
           cat VARCHAR, \
           bug VARCHAR, \
           bzstatus VARCHAR, \
           bzresolution VARCHAR, \
           notes VARCHAR, \
           abenistatus VARCHAR \
           )"
        self.cursor.execute(cmd)
        self.connection.commit()

    def SaveInfo(self):
        p = self.parent.GetP()
        cat = self.parent.panelMain.Category.GetValue()
        package = self.parent.panelMain.Package.GetValue()
        bug, notes, bzstatus, bzresolution = self.GetValues()
        abenistatus = '1'
        if self.new:
            self.cursor.execute("INSERT INTO ebuilds(p, package, cat, bug, bzstatus, bzresolution, notes, abenistatus) \
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
                % (p, package, cat, bug, bzstatus, bzresolution, notes, abenistatus)\
                )
        else:
            self.cursor.execute("UPDATE ebuilds SET p='%s', package='%s', cat='%s', bug='%s', bzstatus='%s',  \
                                bzresolution='%s', notes='%s', abenistatus='%s' WHERE p='%s'" \
                                % (p, package, cat, bug, bzstatus, bzresolution, notes, abenistatus, p))
        self.connection.commit()

    def LoadInfo(self):
        P = self.parent.GetP()
        cat = self.parent.panelMain.Category.GetValue()
        package = self.parent.panelMain.Package.GetValue()
        self.cursor.execute("SELECT p, package, cat, bug, bzstatus, bzresolution, notes, abenistatus \
                                FROM ebuilds WHERE p='%s'" % P)
        data = self.cursor.fetchall()
        if data:
            self.new = 0
            self.FillForm(data)
        else:
            self.new = 1

    def FillForm(self, data):
        p, package, cat, bug, bzstatus, bzresolution, notes, abenistatus = data[0]
        self.BugNbr.SetValue(bug)
        self.NotestextCtrl.SetValue(notes)
        if bzstatus != '':
            self.StatusCombo.SetValue(bzstatus)
        if bzresolution != '':
            self.ResolutionCombo.SetValue(bzresolution)

    def _init_ctrls(self, prnt):
        self.parent = prnt
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_BUGZILLA, name='Bugzilla', parent=prnt,
              pos=wxPoint(278, 137), size=wxSize(462, 493),
              style=wxDEFAULT_DIALOG_STYLE, title='Bugzilla Info & Notes')
        self.SetClientSize(wxSize(462, 493))

        self.BugNbrstaticText = wxStaticText(id=wxID_BUGZILLABUGNBRSTATICTEXT,
              label='Bug Number', name='BugNbrstaticText', parent=self,
              pos=wxPoint(16, 48), size=wxSize(88, 24), style=0)

        self.BugNbr = wxTextCtrl(id=wxID_BUGZILLABUGNBR, name='BugNbr',
              parent=self, pos=wxPoint(96, 48), size=wxSize(120, 22), style=0,
              value='')

        self.SearchButton = wxButton(id=wxID_BUGZILLASEARCHBUTTON,
              label='Search', name='SearchButton', parent=self, pos=wxPoint(226,
              48), size=wxSize(80, 22), style=0)
        self.SearchButton.SetToolTipString('Launch browser, bugs.gentoo.org, find bug')
        EVT_BUTTON(self, wxID_BUGZILLASEARCHBUTTON, self.OnSearchButton)

        self.NotestextCtrl = wxTextCtrl(id=wxID_BUGZILLANOTESTEXTCTRL,
              name='NotestextCtrl', parent=self, pos=wxPoint(16, 168),
              size=wxSize(432, 248), style=wxTAB_TRAVERSAL | wxTE_MULTILINE,
              value='')
        #self.NotestextCtrl.SetToolTipString('Notes')

        self.OK = wxGenButton(ID=wxID_OK, label='OK', name='OK',
              parent=self, pos=wxPoint(112, 432), size=wxSize(81, 27), style=0)

        self.Cancel = wxGenButton(ID=wxID_CANCEL, label='Cancel',
              name='Cancel', parent=self, pos=wxPoint(272, 432), size=wxSize(81,
              27), style=0)

        self.BuzillaStaticBox = wxStaticBox(id=wxID_BUGZILLABUZILLASTATICBOX,
              label='Bugzilla Information', name='BuzillaStaticBox',
              parent=self, pos=wxPoint(8, 8), size=wxSize(448, 128), style=0)

        statusList = ['NEW', 'UNCONFIRMED', 'ASSIGNED', 'REOPENED', 'RESOLVED', 'VERIFIED', 'CLOSED']
        self.StatusCombo = wxComboBox(id=wxID_BUGZILLASTATUSCOMBO,
              name='StatusCombo', parent=self, pos=wxPoint(16, 88),
              size=wxSize(200, 22), style=0, validator=wxDefaultValidator, choices=statusList)
        self.StatusCombo.SetLabel('')

        resolutionList = ['FIXED', 'INVALID', 'WONTFIX', 'LATER', 'REMIND', 'DUPLICATE', 'WORKSFORME']
        self.ResolutionCombo = wxComboBox(
              id=wxID_BUGZILLARESOLUTIONCOMBO, name='ResolutionCombo',
              parent=self, pos=wxPoint(224, 88), size=wxSize(224, 22), style=0,
              validator=wxDefaultValidator, choices=resolutionList)
        self.ResolutionCombo.SetLabel('')

        self.NotesStaticBox = wxStaticBox(id=wxID_BUGZILLANOTESSTATICBOX,
              label='Notes', name='NotesStaticBox', parent=self, pos=wxPoint(8,
              144), size=wxSize(448, 280), style=0)

    def OnSearchButton(self, event):
        bugNbr, foo, foo, foo = self.GetValues()
        URL = "http://bugs.gentoo.org/show_bug.cgi?id=%s" % bugNbr
        os.system("%s %s &" % (self.parent.pref['browser'], URL))

    def GetValues(self):
        bug = self.BugNbr.GetValue()
        notes = self.NotestextCtrl.GetValue()
        status = self.StatusCombo.GetStringSelection()
        resolution = self.ResolutionCombo.GetStringSelection()
        return bug, notes, status, resolution

class GetURIDialog(wxDialog):

    """Dialog box that pops up for URI"""

    def __init__(self, parent, ID, title,
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxDEFAULT_DIALOG_STYLE):
        provider = wxSimpleHelpProvider()
        wxHelpProvider_Set(provider)

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

        label = wxStaticText(self, -1, "Package URI:")
        label.SetHelpText("Enter the URI for the package or 'CVS' for cvs eclass template.")
        box.Add(label, 0, wxALIGN_CENTRE|wxALL, 5)


        self.URI = wxTextCtrl(self, -1, "", size=(280,-1))
        self.URI.SetHelpText("Enter the URI for the package or 'CVS' for cvs eclass template.")
        box.Add(self.URI, 1, wxALIGN_CENTRE|wxALL, 5)

        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)

        box = wxBoxSizer(wxHORIZONTAL)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        text = wxStaticText(self, -1, "Enter CVS for CVS eclass template.")
        sizer.Add(text, 0, wxALIGN_CENTER|wxALL, 5)
        sizer.Add(line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxRIGHT|wxTOP, 5)
        box = wxBoxSizer(wxHORIZONTAL)
        btn = wxButton(self, wxID_OK, " OK ")
        btn.SetDefault()
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        btn = wxButton(self, wxID_CANCEL, " Cancel ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        btn = wxContextHelpButton(self)
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        sizer.AddSizer(box, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)


class EmergeDialog(wxDialog):

    """Dialog box for running emerge with options"""

    def __init__(self, parent, ID, title,
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxDEFAULT_DIALOG_STYLE):
        provider = wxSimpleHelpProvider()
        wxHelpProvider_Set(provider)

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

        self.use = wxTextCtrl(self, -1, parent.pref["use"], size=(280,-1))
        self.use.SetHelpText("Enter any USE variables for the emerge command.")
        box.Add(self.use, 1, wxALIGN_CENTRE|wxALL, 5)

        featuresLabel = wxStaticText(self, -1, "FEATURES=")
        featuresLabel.SetHelpText("Enter any variables for FEATURES.")
        box.Add(featuresLabel, 0, wxALIGN_CENTRE|wxALL, 5)

        self.features = wxTextCtrl(self, -1, parent.pref["features"], size=(280,-1))
        self.features.SetHelpText("Enter any variables for FEATURES.")
        box.Add(self.features, 1, wxALIGN_CENTRE|wxALL, 5)

        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)

        box = wxBoxSizer(wxHORIZONTAL)
        cmd = "emerge %s" % parent.filename
        self.emerge = wxTextCtrl(self, -1, cmd, size=(560,-1))
        self.emerge.SetHelpText("Enter any options for the emerge command.")
        box.Add(self.emerge, 1, wxALIGN_CENTRE|wxALL, 5)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)

        box = wxBoxSizer(wxHORIZONTAL)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        #text = wxStaticText(self, -1, "Enter CVS for CVS eclass template.")
        #sizer.Add(text, 0, wxALIGN_CENTER|wxALL, 5)
        sizer.Add(line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxRIGHT|wxTOP, 5)
        box = wxBoxSizer(wxHORIZONTAL)
        btn = wxButton(self, wxID_OK, " OK ")
        btn.SetDefault()
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        btn = wxButton(self, wxID_CANCEL, " Cancel ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        btn = wxContextHelpButton(self)
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        sizer.AddSizer(box, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

class Preferences(wxDialog):

    """Modify preferences"""

    def __init__(self, parent, ID, title,
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxDEFAULT_DIALOG_STYLE):

        pre = wxPreDialog()
        pre.SetExtraStyle(wxDIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.this = pre.this

        myOptions = Options()
        self.pref = myOptions.Prefs()
        btnOK = wxButton(self, wxID_OK, " OK ")
        btnOK.SetDefault()
        btnCancel = wxButton(self, wxID_CANCEL, " Cancel ")
        vs = wxBoxSizer(wxVERTICAL)
        box1_title = wxStaticBox( self, -1, "Preferences")
        box1 = wxStaticBoxSizer( box1_title, wxVERTICAL )
        gs = wxGridSizer(9, 2, 2, 8)  # rows, cols, hgap, vgap
        self.browser = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.browser.SetValue(self.pref['browser'])
        self.xterm = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.xterm.SetValue(self.pref['xterm'])
        self.diff = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.diff.SetValue(self.pref['diff'])
        self.editor = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.editor.SetValue(self.pref['editor'])
        self.autoTabs = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.autoTabs.SetValue(self.pref['autoTabs'])
        self.fileBrowser = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.fileBrowser.SetValue(self.pref['fileBrowser'])
        self.features = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.features.SetValue(self.pref['features'])
        self.use = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.use.SetValue(self.pref['use'])
        self.log = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.log.SetValue(self.pref['log'])

        gs.AddMany([
        (wxStaticText(self, -1, "Web browser"), 0, wxALIGN_LEFT),
        (self.browser, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "xterm"), 0, wxALIGN_LEFT),
        (self.xterm, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "GUI diff program"), 0, wxALIGN_LEFT),
        (self.diff, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "External editor"), 0, wxALIGN_LEFT),
        (self.editor, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "Auto tabs (yes/no)"), 0, wxALIGN_LEFT),
        (self.autoTabs, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "File Browser"), 0, wxALIGN_LEFT),
        (self.fileBrowser, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "USE"), 0, wxALIGN_LEFT),
        (self.use, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "FEATURES"), 0, wxALIGN_LEFT),
        (self.features, 0, wxALIGN_RIGHT),

        (wxStaticText(self, -1, "Log (bottom/window)"), 0, wxALIGN_LEFT),
        (self.log, 0, wxALIGN_RIGHT),

        (btnOK, 0, wxALIGN_CENTER),
        (btnCancel, 0, wxALIGN_CENTER)
        ])

        vs.AddSizer(box1, 1, wxALL, 5 )
        box1.AddSizer(gs, 1, wxALL, 5 )
        vs.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(vs)
        self.browser.SetFocus()

[wxID_WXDIALOG1,
 wxID_WXDIALOG1PANEL1, wxID_WXDIALOG1RADIOBUTTON1, wxID_WXDIALOG1RADIOBUTTON2,
 wxID_WXDIALOG1RADIOBUTTON3, wxID_WXDIALOG1RADIOBUTTON4,
 wxID_WXDIALOG1RADIOBUTTON5, wxID_WXDIALOG1STATICLINE1,
 wxID_WXDIALOG1STATICLINE2, wxID_WXDIALOG1STATICTEXT1,
 wxID_WXDIALOG1TEXTCTRL1,
] = map(lambda _init_ctrls: wxNewId(), range(11))

class NewFunction(wxDialog):

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_WXDIALOG1, name='', parent=prnt,
              pos=wxPoint(373, 191), size=wxSize(327, 307),
              style=wxDEFAULT_DIALOG_STYLE, title='New Function')

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

