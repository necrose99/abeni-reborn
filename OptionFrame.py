import string, os
from wxPython.wx import *
from options import *


class OptionFrame(wxFrame):
    """TODO: Change this to wxDialog"""
    def __init__(self, parent, id, title):

        myOptions = Options()
        self.pref = myOptions.Prefs()

        wxFrame.__init__(self,parent, -1, title,wxDefaultPosition, wxSize(450,260))
        panel = wxPanel(self, -1,style=wxTAB_TRAVERSAL)
        buttonok = wxButton(panel, 1002, "Ok")
        buttonok.SetPosition(wxPoint(105, 220))

        button = wxButton(panel, 1003, "Cancel")
        button.SetPosition(wxPoint(255, 220))

        EVT_BUTTON(self, 1002, self.OnOK)
        EVT_BUTTON(self, 1003, self.OnCloseMe)
        EVT_CLOSE(self, self.OnCloseWindow)

        row = 20
        col = 175
        width = 260

        row = row + 30
        wxStaticText(panel, -1, "Web browser", wxPoint(15, row), wxSize(145, 20))
        self.browser = wxTextCtrl(panel, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))
        self.browser.SetValue(self.pref['browser'])

        row = row + 30
        wxStaticText(panel, -1, "xterm", wxPoint(15, row), wxSize(145, 20))
        self.xterm = wxTextCtrl(panel, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))
        self.xterm.SetValue(self.pref['xterm'])

        row = row + 30
        wxStaticText(panel, -1, "GUI diff program", wxPoint(15, row), wxSize(145, 20))
        self.diff = wxTextCtrl(panel, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))
        self.diff.SetValue(self.pref['diff'])

        row = row + 30
        wxStaticText(panel, -1, "External editor", wxPoint(15, row), wxSize(145, 20))
        self.editor = wxTextCtrl(panel, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))
        self.editor.SetValue(self.pref['editor'])


    def OnOK(self, event):
        """Write file on OK button"""
        f = open(os.path.expanduser('~/.abeni/abenirc'), 'w')
        f.write('browser = %s\n' % self.browser.GetValue())
        f.write('xterm = %s\n' % self.xterm.GetValue())
        f.write('diff = %s\n' % self.diff.GetValue())
        f.write('editor = %s\n' % self.editor.GetValue())
        f.close()
        self.Close(true)

    def OnCloseMe(self, event):
        """Close window"""
        self.Close(true)

    def OnCloseWindow(self, event):
        """Destroy window"""
        self.Destroy()
