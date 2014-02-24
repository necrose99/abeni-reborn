from wxPython.wx import *

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
