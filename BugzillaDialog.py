import os

from wxPython.wx import *

import utils

[wxID_BUGZILLA, wxID_BUGZILLAABENICOMBOBOX, wxID_BUGZILLAABENISTATICBOX,
 wxID_BUGZILLABUGNBR, wxID_BUGZILLABUGNBRSTATICTEXT,
 wxID_BUGZILLABUZILLASTATICBOX, wxIDCANCEL, wxID_BUGZILLACHECKBOX1,
 wxID_BUGZILLANOTESSTATICBOX, wxID_BUGZILLANOTESTEXTCTRL, wxID_BUGZILLAOK,
 wxID_BUGZILLAPACKAGETEXT, wxID_BUGZILLARESOLUTIONCOMBO,
 wxID_BUGZILLASEARCHBUTTON, wxID_BUGZILLASTATUSCOMBO,
] = map(lambda _init_ctrls: wxNewId(), range(15))


class BugzillaDialog(wxDialog):
    def __init__(self, parent):
        self._init_ctrls(parent)
        loc = os.path.expanduser('~/.abeni/bugz')
        if not os.path.exists("%s/EBUILDS.grl" % loc):
            self.parent.write("Creating project database and tables...")
            self.createDB()
            self.parent.write("Database created.")
        else:
            loc = os.path.expanduser('~/.abeni/bugz')
            self.connection = gadfly.gadfly("bugzDB", loc)
            self.cursor = self.connection.cursor()
        self.LoadInfo()

    def createDB(self):
        self.connection = gadfly.gadfly()
        loc = os.path.expanduser('~/.abeni/bugz')
        self.connection.startup("bugzDB", loc)
        self.cursor = self.connection.cursor()
        cmd = "create table ebuilds (\
           p VARCHAR, \
           package VARCHAR, \
           cat VARCHAR, \
           bug VARCHAR, \
           bzstatus VARCHAR, \
           bzresolution VARCHAR, \
           notes VARCHAR, \
           mine INTEGER, \
           abenistatus VARCHAR \
           )"
        self.cursor.execute(cmd)
        self.connection.commit()

    def SaveInfo(self):
        cat = utils.GetCat(self.parent)
        package = utils.GetPackageName(self.parent)
        p = utils.GetP(self.parent)
        bug, notes, bzstatus, bzresolution, mine, abenistatus = self.GetValues()
        if not bug.isdigit():
            bug = ''
        if self.new:
            self.cursor.execute("INSERT INTO ebuilds(p, package, cat, bug, bzstatus, bzresolution, notes, mine, abenistatus) \
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', %i, '%s')" \
                % (p, package, cat, bug, bzstatus, bzresolution, notes, mine, abenistatus)\
                )
        else:
            self.cursor.execute("UPDATE ebuilds SET p='%s', package='%s', cat='%s', bug='%s', bzstatus='%s',  \
                                bzresolution='%s', notes='%s', mine=%i, abenistatus='%s' WHERE p='%s'" \
                                % (p, package, cat, bug, bzstatus, bzresolution, notes, mine, abenistatus, p))
        self.connection.commit()

    def LoadInfo(self):
        P = utils.GetP(self.parent)
        cat = utils.GetCat(self.parent)
        package = utils.GetPackageName(self.parent)
        self.cursor.execute("SELECT p, package, cat, bug, bzstatus, bzresolution, notes, mine, abenistatus \
                                FROM ebuilds WHERE p='%s'" % P)
        data = self.cursor.fetchall()
        if data:
            self.new = 0
            self.FillForm(data)
        else:
            self.new = 1

    def FillForm(self, data):
        p, package, cat, bug, bzstatus, bzresolution, notes, mine, abenistatus = data[0]
        self.BugNbr.SetValue(bug)
        self.NotestextCtrl.SetValue(notes)
        if bzstatus != '':
            self.StatusCombo.SetValue(bzstatus)
        if bzresolution != '':
            self.ResolutionCombo.SetValue(bzresolution)
        if mine:
            self.checkBox1.SetValue(1)
        if abenistatus != '':
            self.AbeniComboBox.SetValue(abenistatus)

    def _init_ctrls(self, prnt):
        self.parent = prnt
        # generated method, don't edit

        wxDialog.__init__(self, id=wxID_BUGZILLA, name='Bugzilla', parent=prnt,
              pos=wxPoint(306, 74), size=wxSize(462, 548),
              style=wxDEFAULT_DIALOG_STYLE, title='Bugzilla Info & Notes')

        self.SetClientSize(wxSize(462, 548))

        self.BugNbrstaticText = wxStaticText(id=wxID_BUGZILLABUGNBRSTATICTEXT,
              label='Bug Number', name='BugNbrstaticText', parent=self,
              pos=wxPoint(16, 48), size=wxSize(88, 24), style=0)

        self.BugNbr = wxTextCtrl(id=wxID_BUGZILLABUGNBR, name='BugNbr',
              parent=self, pos=wxPoint(96, 48), size=wxSize(120, 22), style=0,
              value='')

        self.SearchButton = wxButton(id=wxID_BUGZILLASEARCHBUTTON,
              label='Get Bug#', name='SearchButton', parent=self,
              pos=wxPoint(226, 48), size=wxSize(126, 22), style=0)
        EVT_BUTTON(self, wxID_BUGZILLASEARCHBUTTON, self.OnSearchButton)

        self.NotestextCtrl = wxTextCtrl(id=wxID_BUGZILLANOTESTEXTCTRL,
              name='NotestextCtrl', parent=self, pos=wxPoint(16, 228),
              size=wxSize(432, 264), style=wxTAB_TRAVERSAL | wxTE_MULTILINE,
              value='')
        self.NotestextCtrl.SetToolTipString('')

        self.OK = wxGenButton(ID=wxID_OK, label='OK', name='OK',
              parent=self, pos=wxPoint(22, 512), size=wxSize(81, 27), style=0)

        SubID = wxNewId()
        self.Submit = wxGenButton(ID=SubID, label='Submit to Bugzilla', name='Submit',
              parent=self, pos=wxPoint(112, 512), size=wxSize(180, 27), style=0)
        EVT_BUTTON(self.Submit, SubID, self.OnSubmitButton)

        self.Cancel = wxGenButton(self, ID=wxID_CANCEL, label='Cancel',
              pos=wxPoint(330, 512), size=wxSize(81, 27))

        self.BuzillaStaticBox = wxStaticBox(id=wxID_BUGZILLABUZILLASTATICBOX,
              label='Bugzilla Information', name='BuzillaStaticBox',
              parent=self, pos=wxPoint(10, 8), size=wxSize(448, 114), style=0)

        statusList = ['', 'NEW', 'UNCONFIRMED', 'ASSIGNED', 'REOPENED', 'RESOLVED', 'VERIFIED', 'CLOSED']
        self.StatusCombo = wxComboBox(choices=statusList, id=wxID_BUGZILLASTATUSCOMBO,
              name='StatusCombo', parent=self, pos=wxPoint(16, 88),
              size=wxSize(200, 22), style=0, validator=wxDefaultValidator,
              value='')

        resolutionList = ['', 'FIXED', 'INVALID', 'WONTFIX', 'LATER', 'REMIND', 'DUPLICATE', 'WORKSFORME']
        self.ResolutionCombo = wxComboBox(choices=resolutionList,
              id=wxID_BUGZILLARESOLUTIONCOMBO, name='ResolutionCombo',
              parent=self, pos=wxPoint(224, 88), size=wxSize(224, 22), style=0,
              validator=wxDefaultValidator, value='')

        self.NotesStaticBox = wxStaticBox(id=wxID_BUGZILLANOTESSTATICBOX,
              label='Notes', name='NotesStaticBox', parent=self, pos=wxPoint(8,
              208), size=wxSize(448, 296), style=0)

        self.AbeniStaticBox = wxStaticBox(id=wxID_BUGZILLAABENISTATICBOX,
              label='Abeni Information', name='AbeniStaticBox', parent=self,
              pos=wxPoint(8, 132), size=wxSize(450, 64), style=0)

        self.PackageText = wxStaticText(id=wxID_BUGZILLAPACKAGETEXT,
              label='Ebuild Package', name='PackageText', parent=self,
              pos=wxPoint(228, 20), size=wxSize(88, 16), style=0)

        abeniList = [''] + Options().Prefs()['statuslist'].split(',')
        self.AbeniComboBox = wxComboBox(choices=abeniList,
              id=wxID_BUGZILLAABENICOMBOBOX, name='AbeniComboBox', parent=self,
              pos=wxPoint(224, 160), size=wxSize(224, 22), style=0,
              validator=wxDefaultValidator, value='')

        self.checkBox1 = wxCheckBox(id=wxID_BUGZILLACHECKBOX1,
              label='Ebuild is Mine', name='checkBox1', parent=self,
              pos=wxPoint(24, 160), size=wxSize(144, 24), style=0)
        self.checkBox1.SetValue(False)

    def OnSubmitButton(self, event):
            #import time
            bugNbr = self.BugNbr.GetValue()
            if not bugNbr:
                bugNbr = 0
            win = SubmitEbuild(self, self.parent, bugNbr)
            win.ShowModal()
            win.Destroy()
            if win.bugNbr:
                self.BugNbr.SetValue(win.bugNbr)
                pos = self.AbeniComboBox.FindString("SUBMITTED")
                self.AbeniComboBox.SetSelection(pos)
                pos = self.StatusCombo.FindString("NEW")
                self.StatusCombo.SetSelection(pos)
                self.checkBox1.SetValue(True)
                txt = self.NotestextCtrl.GetValue()
                now = time.asctime(time.localtime())
                self.NotestextCtrl.SetValue(txt + ("Ebuild submitted %s" % now))
            else:
                self.MyMessage("Failed to create bug.", "Error", "error")

    def MyMessage(self, msg, title, type="info"):
        """Simple informational dialog"""
        if type == "info":
            icon = wxICON_INFORMATION
        elif type == "error":
            icon = wxICON_ERROR

        dlg = wxMessageDialog(self, msg, title, wxOK | icon)
        dlg.ShowModal()
        dlg.Destroy()

    def OnSearchButton(self, event):
        """Launches browser and searches bugzilla"""
        myOptions = Options()
        pref = myOptions.Prefs()
        bugNbr, foo, foo, foo, foo, foo = self.GetValues()
        if bugNbr.isdigit():
            URL = "http://bugs.gentoo.org/show_bug.cgi?id=%s" % bugNbr
            if pref['browser']:
                os.system("%s %s &" % (pref['browser'], URL))
            else:
                self.MyMessage("You need to set your browser in preferences", "Error", "error")
        else:
            self.MyMessage("Enter a number", "Error", "error")

    def GetValues(self):
        bug = self.BugNbr.GetValue()
        notes = self.NotestextCtrl.GetValue()
        status = self.StatusCombo.GetStringSelection()
        resolution = self.ResolutionCombo.GetStringSelection()
        mine = self.checkBox1.GetValue()
        if mine:
            mine = 1
        else:
            mine = 0
        abenistatus = self.AbeniComboBox.GetStringSelection()
        return bug, notes, status, resolution, mine, abenistatus
