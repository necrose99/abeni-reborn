import string, os
from wxPython.wx import *
from options import *

appdir = os.path.abspath(os.path.join(os.getcwd(), sys.path[0]))

class OptionFrame(wxFrame):
    def __init__(self, parent, id, title):

        myOptions = Options()
        self.pref = myOptions.Prefs()
        self.debug = self.pref['debug']

        wxFrame.__init__(self,parent, -1, title,wxDefaultPosition, wxSize(450,460))
        panel = wxPanel(self, -1,style=wxTAB_TRAVERSAL)
        buttonok = wxButton(panel, 1002, "Ok")
        buttonok.SetPosition(wxPoint(105, 430))

        button = wxButton(panel, 1003, "Cancel")
        button.SetPosition(wxPoint(255, 430))

        EVT_BUTTON(self, 1002, self.OnOK)
        EVT_BUTTON(self, 1003, self.OnCloseMe)
        EVT_CLOSE(self, self.OnCloseWindow)

        row = 20
        col = 175
        width = 260

        row = row + 30
        wxStaticText(panel, -1, "Debug 1=yes 0=no", wxPoint(15, row), wxSize(145, 20))
        self.Inpdebug = wxTextCtrl(panel, wxNewId(), "", wxPoint(col, row), wxSize(width, 20))

        self.Inpdebug.SetValue(self.debug)

    def OnOK(self, event):
        f = open(('%s/abenirc' % appdir), 'w')
        f.write('debug = %s\n' % self.Inpdebug.GetValue())
        f.close()
        self.Close(true)

    def OnCloseMe(self, event):
        self.Close(true)

    def OnCloseWindow(self, event):
        self.Destroy()
