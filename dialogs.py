import os
import gadfly
import time
import sys

from wxPython.wx import *
from wxPython.help import *
from wxPython.lib.grids import wxGridSizer, wxFlexGridSizer
from wxPython.lib.buttons import *
from wxPython.stc import *
from wxPython.html import *
import wx   # This module uses the new wx namespace
import wx.html
import wx.lib.wxpTag
from options import *

import utils
import __version__

#---------------------------------------------------------------------------

class MyAboutBox(wx.Dialog):
    text = '''
<html>
<body bgcolor="#dddaec">
<center><table bgcolor="#7a5ada" width="100%%" cellspacing="0"
cellpadding="0" border="1">
<tr>
    <td align="center">
    <font color="#ffffff">
    <h1>Abeni %s</h1>
    Python %s<br>
    wxPython %s<br> 
    </font">
    </td>
</tr>
</table>

<p><b>Abeni</b> is an IDE for creating ebuilds for 
Gentoo Linux</p>

<p><b>Abeni</b> was written by <b>Rob Cakebread</b> <br>
<b>with contributions from Marius Mauch. </b> <br><br>
<b>Abeni</b> is Copyright (c) 2003-2004 Rob Cakebread <pythonhead@gentoo.org>.</p>

<p>
<font size="-1"><b>Abeni</b> is released under the terms of<br>
the GNU Public License v.2</font>
</p>

<p><wxp module="wx" class="Button">
    <param name="label" value="Okay">
    <param name="id"    value="ID_OK">
</wxp></p>
</center>
</body>
</html>
'''
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'About Abeni',)
        html = wx.html.HtmlWindow(self, -1, size=(420, -1))
        py_version = sys.version.split()[0]
        html.SetPage(self.text % (__version__.version, py_version, wx.VERSION_STRING))
        btn = html.FindWindowById(wx.ID_OK)
        btn.SetDefault()
        ir = html.GetInternalRepresentation()
        html.SetSize( (ir.GetWidth()+25, ir.GetHeight()+25) )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)

#---------------------------------------------------------------------------



if __name__ == '__main__':
    app = wx.PySimpleApp()
    dlg = MyAboutBox(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()

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


[wxID_SUBMITEBUILD, wxID_SUBMITEBUILDCANCELBUTTON,
 wxID_SUBMITEBUILDDESCRIPTIONSTATICTEXT, wxID_SUBMITEBUILDDESCTEXTCTRL,
 wxID_SUBMITEBUILDSEARCHBUTTON, wxID_SUBMITEBUILDSTATICBOX1,
 wxID_SUBMITEBUILDSUBMITBUTTON, wxID_SUBMITEBUILDSUMMARYSTATICTEXT,
 wxID_SUBMITEBUILDSUMMARYTEXTCTRL,
] = map(lambda _init_ctrls: wxNewId(), range(9))

class SubmitEbuild(wxDialog):

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, id=wxID_SUBMITEBUILD, name='SubmitEbuild',
              parent=prnt, pos=wxPoint(267, 105), size=wxSize(548, 457),
              style=wxDEFAULT_DIALOG_STYLE, title='Submit Bug to Bugzilla')
        self.SetClientSize(wxSize(548, 457))

        self.staticBox1 = wxStaticBox(id=wxID_SUBMITEBUILDSTATICBOX1,
              label='Submit Ebuild to Bugzilla', name='staticBox1', parent=self,
              pos=wxPoint(8, 8), size=wxSize(528, 392), style=0)

        self.DesctextCtrl = wxTextCtrl(id=wxID_SUBMITEBUILDDESCTEXTCTRL,
              name='DesctextCtrl', parent=self, pos=wxPoint(24, 112),
              size=wxSize(496, 272), style=wxTE_MULTILINE, value='')

        self.SummarytextCtrl = wxTextCtrl(id=wxID_SUBMITEBUILDSUMMARYTEXTCTRL,
              name='SummarytextCtrl', parent=self, pos=wxPoint(88, 48),
              size=wxSize(432, 22), style=0, value='')

        self.SummarystaticText = wxStaticText(id=wxID_SUBMITEBUILDSUMMARYSTATICTEXT,
              label='Summary', name='SummarystaticText', parent=self,
              pos=wxPoint(24, 56), size=wxSize(51, 16), style=0)

        self.DescriptionstaticText = wxStaticText(id=wxID_SUBMITEBUILDDESCRIPTIONSTATICTEXT,
              label='Description', name='DescriptionstaticText', parent=self,
              pos=wxPoint(28, 90), size=wxSize(63, 16), style=0)

        self.Searchbutton = wxButton(id=wxID_SUBMITEBUILDSEARCHBUTTON,
              label='Search for Duplicates', name='Searchbutton', parent=self,
              pos=wxPoint(56, 416), size=wxSize(136, 22), style=0)
        self.Searchbutton.SetBackgroundColour(wxColour(255, 0, 0))

        self.Submitbutton = wxButton(id=wxID_SUBMITEBUILDSUBMITBUTTON,
              label='Submit', name='Submitbutton', parent=self, pos=wxPoint(256,
              416), size=wxSize(80, 22), style=0)
        EVT_BUTTON(self.Submitbutton, wxID_SUBMITEBUILDSUBMITBUTTON,
              self.OnSubmitButton)

        self.Cancelbutton = wxButton(id=wxID_CANCEL,
              label='Cancel', name='Cancelbutton', parent=self, pos=wxPoint(392,
              416), size=wxSize(80, 22), style=0)

    def __init__(self, prnt, parent, bugNbr):
        self._init_ctrls(prnt)
        self.bugNbr = bugNbr
        s = "%s (New Package)" % parent.GetP()
        self.SummarytextCtrl.SetValue(s)
        desc = parent.panelMain.Desc.GetValue()
        if desc.startswith('"') or desc.startswith("'"):
            desc = desc[1:]
        if desc.endswith('"') or desc.endswith("'"):
            desc = desc[:-1]
        self.DesctextCtrl.SetValue(desc)
        self.filename = parent.filename
        self.uri = parent.panelMain.Homepage.GetValue()

    def OnSubmitButton(self, event):
        '''Catch submit event, submit ebuild'''
        self.summary = self.SummarytextCtrl.GetValue()
        self.desc = self.DesctextCtrl.GetValue()
        dlg = wxTextEntryDialog(self, 'Enter your Bugzilla password:',
                            'Bugzilla password', '', style=wxTE_PASSWORD)
        if dlg.ShowModal() == wxID_OK:
            self.password = dlg.GetValue()
            dlg.Destroy()
            self.SubmitEbuild()

    def SubmitEbuild(self):
        ''' Do the actual bug creation and attachment upload'''
        import BugzInterface
        user = Options().Prefs()['email']
        if not user:
            myDlg = self.MyMessage("You need to set your bugzilla email in preferences.", "Error", "error")
            return

        a = BugzInterface.HandleForm(self.filename, self.summary, self.desc, self.uri, self.password, user)
        max = 90
        dlg = wxProgressDialog("Submitting ebuild",
                               "Creating new bug...",
                               max,
                               self,
                               wxPD_CAN_ABORT | wxPD_APP_MODAL)
        count = 5
        dlg.Update(count, "Loging in to bugs.gentoo.org...")
        a.Login()
        count += 33
        if not self.bugNbr:
            dlg.Update(count, "Entering new bug...")
            a.EnterNewBug()
            count += 33
            self.bugNbr = a.bugNbr
        if self.bugNbr:
            dlg.Update(count, "Uploading attachment...")
            a.UploadAttachment()
            count += 22
            dlg.Update(count, "Done.")
        else:
            myDlg = self.MyMessage("Couldn't create bug", "Error", "error")
        dlg.Destroy()
        self.Close()

    def MyMessage(self, msg, title, type="info"):
        """Simple informational dialog"""
        if type == "info":
            icon = wxICON_INFORMATION
        elif type == "error":
            icon = wxICON_ERROR

        dlg = wxMessageDialog(self, msg, title, wxOK | icon)
        dlg.ShowModal()
        dlg.Destroy()



[wxID_BUGZQUERY, wxID_BUGZQUERYBUGNBRBUTTON, wxID_BUGZQUERYBUGNBRSTATICBOX,
 wxIDCANCEL, wxID_BUGZQUERYQUERYBUTTON,
 wxID_BUGZQUERYQUERYSTATICBOX, wxID_BUGZQUERYQUERYSTATICTEXT,
 wxID_BUGZQUERYQUERYTEXTCTRL, wxID_BUGZQUERYTEXTCTRL1,
] = map(lambda _init_ctrls: wxNewId(), range(9))

class BugzQuery(wxDialog):

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_BUGZQUERY, name='BugzQuery',
              parent=prnt, pos=wxPoint(254, 170), size=wxSize(330, 284),
              style=wxDEFAULT_DIALOG_STYLE, title='Bugzilla Query')
        self.SetClientSize(wxSize(330, 284))

        self.BugNbrbutton = wxButton(id=wxID_BUGZQUERYBUGNBRBUTTON,
              label='Fetch', name='BugNbrbutton', parent=self, pos=wxPoint(112,
              48), size=wxSize(120, 22), style=0)
        self.BugNbrbutton.SetToolTipString('')
        EVT_BUTTON(self.BugNbrbutton, wxID_BUGZQUERYBUGNBRBUTTON,
              self.OnBugnbrbuttonButton)

        self.BugNbrstaticBox = wxStaticBox(id=wxID_BUGZQUERYBUGNBRSTATICBOX,
              label='Search by Bug Nbr', name='BugNbrstaticBox', parent=self,
              pos=wxPoint(8, 8), size=wxSize(312, 96), style=0)

        self.textCtrl1 = wxTextCtrl(id=wxID_BUGZQUERYTEXTCTRL1,
              name='textCtrl1', parent=self, pos=wxPoint(16, 48),
              size=wxSize(80, 22), style=0, value='')

        self.QuerystaticBox = wxStaticBox(id=wxID_BUGZQUERYQUERYSTATICBOX,
              label='Query by Search Term', name='QuerystaticBox', parent=self,
              pos=wxPoint(8, 120), size=wxSize(312, 152), style=0)

        self.QuerystaticText = wxStaticText(id=wxID_BUGZQUERYQUERYSTATICTEXT,
              label='Enter search criteria (contains all strings)',
              name='QuerystaticText', parent=self, pos=wxPoint(24, 154),
              size=wxSize(229, 16), style=0)

        self.QuerytextCtrl = wxTextCtrl(id=wxID_BUGZQUERYQUERYTEXTCTRL,
              name='QuerytextCtrl', parent=self, pos=wxPoint(24, 184),
              size=wxSize(280, 22), style=0, value='')

        self.Querybutton = wxButton(id=wxID_BUGZQUERYQUERYBUTTON,
              label='Search', name='Querybutton', parent=self, pos=wxPoint(40,
              232), size=wxSize(112, 22), style=0)
        EVT_BUTTON(self.Querybutton, wxID_BUGZQUERYQUERYBUTTON,
              self.OnQuerybuttonButton)

        self.CancelButton = wxButton(id=wxID_CANCEL,
              label='Cancel', name='CancelButton', parent=self, pos=wxPoint(184,
              232), size=wxSize(104, 22), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def MyMessage(self, msg, title, type="info"):
        """Simple informational dialog"""
        if type == "info":
            icon = wxICON_INFORMATION
        elif type == "error":
            icon = wxICON_ERROR

        dlg = wxMessageDialog(self, msg, title, wxOK | icon)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBugnbrbuttonButton(self, event):
        """Launches browser and searches bugzilla"""
        myOptions = Options()
        pref = myOptions.Prefs()
        bugNbr = self.textCtrl1.GetValue()
        if not bugNbr.isdigit():
            self.MyMessage("Enter a number", "Error", "error")
            return
        URL = "http://bugs.gentoo.org/show_bug.cgi?id=%s" % bugNbr
        if pref['browser']:
            os.system("%s %s &" % (pref['browser'], URL))
        else:
            self.MyMessage("You need to define a browser in preferences.", "Error", "error")

    def OnQuerybuttonButton(self, event):
        """Launches browser and searches bugzilla for string(s)"""
        import urllib
        myOptions = Options()
        pref = myOptions.Prefs()
        t = self.QuerytextCtrl.GetValue()
        t = urllib.quote_plus(t)
        URL = "'http://bugs.gentoo.org/buglist.cgi?query_format=&short_desc_type=allwordssubstr&short_desc=%s'" % t
        if pref['browser']:
            os.system("%s %s &" % (pref['browser'], URL))
        else:
            self.MyMessage("You need to define a browser in preferences.", "Error", "error")

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

class EmergeDialog(wxDialog):

    """Dialog box for running emerge with options"""

    def __init__(self, parent, ID, title,
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxDEFAULT_DIALOG_STYLE):
        provider = wxSimpleHelpProvider()
        wxHelpProvider_Set(provider)
        self.parent = parent
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
        cat_pack = "%s/%s" % (utils.GetCategoryName(parent), utils.GetPackageName(parent))
        #TODO: Get arch from config, add arch as config option ;)
        self.cmd = "ACCEPT_KEYWORDS='~x86' emerge %s" %  cat_pack
        self.pretend_cmd = "FEATURES='%s' USE='%s' ACCEPT_KEYWORDS='~x86' emerge -pv %s" \
                   % (self.features.GetValue(), self.use.GetValue(), cat_pack)
        self.emerge = wxTextCtrl(self, -1, self.cmd, size=(560,-1))
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
        btn = wxButton(self, wxID_OK, " Emerge ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        wxID_PRETEND_EMERGE = wxNewId()
        btn = wxButton(self, wxID_PRETEND_EMERGE, " Pretend ")
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        EVT_BUTTON(btn, wxID_PRETEND_EMERGE, self.OnPretendButton)
        btn = wxButton(self, wxID_CANCEL, " Cancel ")
        btn.SetDefault()
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        btn = wxContextHelpButton(self)
        box.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)
        sizer.AddSizer(box, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def OnPretendButton(self, event):
        """ emerge -pv this ebuild """
        utils.write(self, self.pretend_cmd)
        utils.ExecuteInLog(self.parent, self.pretend_cmd)

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
        self.statuslist = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.statuslist.SetValue(self.pref['statuslist'])
        self.use = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.use.SetValue(self.pref['use'])
        self.features = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.features.SetValue(self.pref['features'])
        self.log = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.log.SetValue(self.pref['log'])
        self.email = wxTextCtrl(self, wxNewId(), "", size=(200,-1))
        self.email.SetValue(self.pref['email'])

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
        (wxStaticText(self, -1, "Abeni status modes"), 0, wxALIGN_LEFT),
        (self.statuslist, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "USE"), 0, wxALIGN_LEFT),
        (self.use, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "FEATURES"), 0, wxALIGN_LEFT),
        (self.features, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "Log (bottom/window)"), 0, wxALIGN_LEFT),
        (self.log, 0, wxALIGN_RIGHT),
        (wxStaticText(self, -1, "Bugzilla Email Addr"), 0, wxALIGN_LEFT),
        (self.email, 0, wxALIGN_RIGHT),

        (btnOK, 0, wxALIGN_CENTER),
        (btnCancel, 0, wxALIGN_CENTER)
        ])

        vs.AddSizer(box1, 1, wxALL, 5 )
        box1.AddSizer(gs, 1, wxALL, 5 )
        vs.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(vs)
        self.browser.SetFocus()

#[wxID_WXDIALOG1,
# wxID_WXDIALOG1PANEL1, wxID_WXDIALOG1RADIOBUTTON1, wxID_WXDIALOG1RADIOBUTTON2,
# wxID_WXDIALOG1RADIOBUTTON3, wxID_WXDIALOG1RADIOBUTTON4,
# wxID_WXDIALOG1RADIOBUTTON5, wxID_WXDIALOG1STATICLINE1,
# wxID_WXDIALOG1STATICLINE2, wxID_WXDIALOG1STATICTEXT1,
# wxID_WXDIALOG1TEXTCTRL1,
#] = map(lambda _init_ctrls: wxNewId(), range(11))

#class NewFunction(wxDialog):

#    def _init_ctrls(self, prnt):
#        # generated method, don't edit
#        wxDialog.__init__(self, id=wxID_WXDIALOG1, name='', parent=prnt,
#              pos=wxPoint(373, 191), size=wxSize(327, 307),
#              style=wxDEFAULT_DIALOG_STYLE, title='New Function')

#        self.SetClientSize(wxSize(327, 307))

#        self.panel1 = wxPanel(id=wxID_WXDIALOG1PANEL1, name='panel1',
#              parent=self, pos=wxPoint(0, 0), size=wxSize(327, 307),
#              style=wxTAB_TRAVERSAL)

#        self.staticText1 = wxStaticText(id=wxID_WXDIALOG1STATICTEXT1,
#              label='Function Name', name='staticText1', parent=self.panel1,
#              pos=wxPoint(16, 26), size=wxSize(96, 16), style=0)

#        self.textCtrl1 = wxTextCtrl(id=wxID_WXDIALOG1TEXTCTRL1,
#              name='textCtrl1', parent=self.panel1, pos=wxPoint(112, 24),
#              size=wxSize(176, 22), style=0, value='()')

#        self.radioButton1 = wxRadioButton(id=wxID_WXDIALOG1RADIOBUTTON1,
#              label='empty', name='radioButton1', parent=self.panel1,
#              pos=wxPoint(32, 82), size=wxSize(94, 24), style=0)
#        self.radioButton1.SetValue(True)
#        EVT_RADIOBUTTON(self.radioButton1, wxID_WXDIALOG1RADIOBUTTON1,
#              self.OnRadiobutton1Radiobutton)

#        self.radioButton2 = wxRadioButton(id=wxID_WXDIALOG1RADIOBUTTON2,
#              label='src_compile - empty', name='radioButton2',
#              parent=self.panel1, pos=wxPoint(32, 104), size=wxSize(256, 32),
#              style=0)
#        self.radioButton2.SetValue(False)
#        EVT_RADIOBUTTON(self.radioButton2, wxID_WXDIALOG1RADIOBUTTON2,
#              self.OnRadiobutton2Radiobutton)

#        self.radioButton3 = wxRadioButton(id=wxID_WXDIALOG1RADIOBUTTON3,
#              label='src_compile - ./configure - make', name='radioButton3',
#              parent=self.panel1, pos=wxPoint(32, 132), size=wxSize(256, 24),
#              style=0)
#        self.radioButton3.SetValue(False)
#        EVT_RADIOBUTTON(self.radioButton3, wxID_WXDIALOG1RADIOBUTTON3,
#              self.OnRadiobutton3Radiobutton)

#        self.radioButton4 = wxRadioButton(id=wxID_WXDIALOG1RADIOBUTTON4,
#              label='src_install - make install', name='radioButton4',
#              parent=self.panel1, pos=wxPoint(32, 158), size=wxSize(264, 24),
#              style=0)
#        self.radioButton4.SetValue(False)
#        EVT_RADIOBUTTON(self.radioButton4, wxID_WXDIALOG1RADIOBUTTON4,
#              self.OnRadiobutton4Radiobutton)

#        self.radioButton5 = wxRadioButton(id=wxID_WXDIALOG1RADIOBUTTON5,
#              label='src_install - python setup.py install',
#              name='radioButton5', parent=self.panel1, pos=wxPoint(32, 184),
#              size=wxSize(264, 24), style=0)
#        self.radioButton5.SetValue(False)
#        EVT_RADIOBUTTON(self.radioButton5, wxID_WXDIALOG1RADIOBUTTON5,
#              self.OnRadiobutton5Radiobutton)

#        self.staticLine1 = wxStaticLine(id=wxID_WXDIALOG1STATICLINE1,
#              name='staticLine1', parent=self.panel1, pos=wxPoint(8, 56),
#              size=wxSize(312, 20), style=0)

#        self.staticLine2 = wxStaticLine(id=wxID_WXDIALOG1STATICLINE2,
#              name='staticLine2', parent=self.panel1, pos=wxPoint(8, 224),
#              size=wxSize(312, 4), style=0)

#        self.button1 = wxButton(id=wxID_OK, label='OK',
#              name='button1', parent=self.panel1, pos=wxPoint(48, 256),
#              size=wxSize(80, 22), style=0)
#        self.button1.SetDefault()

#        self.button2 = wxButton(id=wxID_CANCEL, label='Cancel',
#              name='button2', parent=self.panel1, pos=wxPoint(184, 256),
#              size=wxSize(80, 22), style=0)

#    def __init__(self, parent):
#        """Populate panel with controls"""
#        self._init_ctrls(parent)
#        self.val = None
#        self.textCtrl1.SetFocus()
import add_function_dialog
class NewFunction(add_function_dialog.AddFunction):
     def GetFunc(self):
         """Returns function name and function body"""
         return self.func, self.val

#    def GetFunc(self):
#        """Returns function name and function body"""
#        self.func = self.textCtrl1.GetValue()
#        if self.val == None:
#            self.val = self.func + ' {\n\n}\n'
#        return self.func, self.val

#    def OnRadiobutton1Radiobutton(self, event):
#        """empty custom function"""
#        self.textCtrl1.SetValue('()')
#        self.textCtrl1.SetFocus()
#        self.val = None

#    def OnRadiobutton2Radiobutton(self, event):
#        """src_compile - empty"""
#        name = 'src_compile()'
#        self.textCtrl1.SetValue(name)
#        self.val = None

#    def OnRadiobutton3Radiobutton(self, event):
#        """src_compile - configure/make"""
#        name = 'src_compile()'
#        self.textCtrl1.SetValue(name)
#        self.val = name + ' {\n\teconf || die\n\temake || die\n}\n'

#    def OnRadiobutton4Radiobutton(self, event):
#        """src_install - make install"""
#        name = 'src_install()'
#        self.textCtrl1.SetValue(name)
#        self.val = name + ' {\n\teinstall || die\n}\n'

#    def OnRadiobutton5Radiobutton(self, event):
#        """src_install - python setup.py install"""
#        name = 'src_install()'
#        self.textCtrl1.SetValue(name)
#        self.val = name + ' {\n\tpython setup.py install || die\n}\n'


class EchangelogDialog(wxDialog):

    """Dialog box for echangelog"""

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

        label = wxStaticText(self, -1, "echangelog")
        label.SetHelpText("Enter text to pass to echangelog. Leave blank for multi-line entry (xterm will be launched).")
        box.Add(label, 0, wxALIGN_CENTRE|wxALL, 5)
        self.inp = wxTextCtrl(self, -1, "", size=(280,-1))
        self.inp.SetHelpText("Enter text to pass to echangelog. Leave blank for multi-line entry (xterm will be launched).")
        box.Add(self.inp, 1, wxALIGN_CENTRE|wxALL, 5)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)

        box = wxBoxSizer(wxHORIZONTAL)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
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
        label.SetHelpText("Enter the URI for the package or leave blank for CVS.")
        box.Add(label, 0, wxALIGN_CENTRE|wxALL, 5)
        self.URI = wxTextCtrl(self, -1, "", size=(280,-1))
        self.URI.SetHelpText("Enter the URI for the package or leave blank for CVS.")
        box.Add(self.URI, 1, wxALIGN_CENTRE|wxALL, 5)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        box = wxBoxSizer(wxHORIZONTAL)
        sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        text = wxStaticText(self, -1, "Leave blank if this is a CVS ebuild.")
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

