#Boa:Frame:wxFrame1

import os
import shutil

from wxPython.wx import *

import options

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON2, 
 wxID_WXFRAME1BUTTON3, wxID_WXFRAME1BUTTON4, wxID_WXFRAME1BUTTON5, 
 wxID_WXFRAME1LISTBOX1, wxID_WXFRAME1LISTBOX2, wxID_WXFRAME1PANEL1, 
 wxID_WXFRAME1STATICBOX1, wxID_WXFRAME1STATICBOX2, wxID_WXFRAME1STATICTEXT1, 
] = map(lambda _init_ctrls: wxNewId(), range(12))

class wxFrame1(wxFrame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(100, 96), size=wxSize(754, 439),
              style=wxDEFAULT_FRAME_STYLE, title='Copy/Diff/Edit in ${FILESDIR}')
        self.SetClientSize(wxSize(754, 439))

        self.panel1 = wxPanel(id=wxID_WXFRAME1PANEL1, name='panel1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(754, 439),
              style=wxTAB_TRAVERSAL)
        self.panel1.SetAutoLayout(True)

        self.staticBox1 = wxStaticBox(id=wxID_WXFRAME1STATICBOX1,
              label='${FILESDIR} PORTDIR', name='staticBox1',
              parent=self.panel1, pos=wxPoint(16, 16), size=wxSize(288, 408),
              style=0)

        self.staticBox2 = wxStaticBox(id=wxID_WXFRAME1STATICBOX2,
              label='${FILESDIR} PORTDIR_OVERLAY', name='staticBox2',
              parent=self.panel1, pos=wxPoint(376, 16), size=wxSize(360, 408),
              style=0)

        self.button1 = wxButton(id=wxID_WXFRAME1BUTTON1, label='Copy',
              name='button1', parent=self.panel1, pos=wxPoint(312, 100),
              size=wxSize(56, 24), style=0)
        EVT_BUTTON(self.button1, wxID_WXFRAME1BUTTON1, self.OnButton1Button)

        self.staticText1 = wxStaticText(id=wxID_WXFRAME1STATICTEXT1,
              label='--->', name='staticText1', parent=self.panel1,
              pos=wxPoint(328, 80), size=wxSize(23, 14), style=0)

        self.button2 = wxButton(id=wxID_WXFRAME1BUTTON2, label='Delete',
              name='button2', parent=self.panel1, pos=wxPoint(672, 192),
              size=wxSize(56, 24), style=0)
        EVT_BUTTON(self.button2, wxID_WXFRAME1BUTTON2, self.OnButton2Button)

        self.button5 = wxButton(id=wxID_WXFRAME1BUTTON5, label='Done',
              name='button5', parent=self.panel1, pos=wxPoint(312, 392),
              size=wxSize(56, 24), style=0)
        EVT_BUTTON(self.button5, wxID_WXFRAME1BUTTON5, self.OnButton5Button)

        self.listBox1 = wxListBox(choices=[], id=wxID_WXFRAME1LISTBOX1,
              name='listBox1', parent=self.panel1, pos=wxPoint(24, 40),
              size=wxSize(272, 376), style=wxLB_SINGLE)

        self.listBox2 = wxListBox(choices=[], id=wxID_WXFRAME1LISTBOX2,
              name='listBox2', parent=self.panel1, pos=wxPoint(384, 40),
              size=wxSize(280, 376), style=wxLB_SINGLE)

        self.button3 = wxButton(id=wxID_WXFRAME1BUTTON3, label='Edit',
              name='button3', parent=self.panel1, pos=wxPoint(672, 240),
              size=wxSize(56, 24), style=0)
        EVT_BUTTON(self.button3, wxID_WXFRAME1BUTTON3, self.OnButton3Button)

        self.button4 = wxButton(id=wxID_WXFRAME1BUTTON4, label='Diff',
              name='button4', parent=self.panel1, pos=wxPoint(312, 144),
              size=wxSize(56, 24), style=0)
        EVT_BUTTON(self.button4, wxID_WXFRAME1BUTTON4, self.OnButton4Button)

    def __init__(self, parent, fdir, fdir_olay):
        self._init_ctrls(parent)
        self.fdir = "%s/files" % fdir
        self.fdir_olay = "%s/files" % fdir_olay

        if not os.path.exists(fdir_olay):
            dlg = wxMessageDialog(self, "Nothing in ${FILESDIR}\n\nNo digest yet.", "Error", wxOK)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if not os.path.exists(self.fdir):
            #Disable widgets if package doesn't exist in PORTDIR 
            self.listBox1.Disable()
            self.button1.Disable()
            self.button4.Disable()
            self.staticBox1.Disable()
            self.staticText1.Disable()
        else:
            files = self.GetPortdirFiles()
            for f in files:
                self.listBox1.Append(f)

        files = self.GetOverlayFiles()
        for f in files:
            self.listBox2.Append(f)

    def OnButton1Button(self, event):
        """ Copy file """
        #TODO: If exists, pop up dialog and don't Append to list
        src = "%s/%s" % (self.fdir, self.GetPortdirSelection())
        dest = self.fdir_olay
        if os.path.exists(src):
            if os.path.exists(dest):
                dlg = wxMessageDialog(self, "File already exists in OVERLAY.\n\nOverwrite?", "Error", wxYES_NO)
                v = dlg.ShowModal()
                if v == wxID_YES:
                    shutil.copy(src, dest)
                    return
                else:
                    return
            shutil.copy(src, dest)
            self.listBox2.Append(os.path.basename(src))

    def OnButton2Button(self, event):
        """ Delete file in ${FILESDIR} PORTDIR_OVERLAY """
        f = self.GetOverlaySelection()
        pos = self.listBox2.GetSelection()
        victim = "%s/%s" % (self.fdir_olay, f)
        if os.path.exists(victim):
            #Nothing is selected:
            if os.path.isdir(victim):
                return 
            else:
                os.remove(victim)
                self.listBox2.Delete(pos)
                self.listBox2.SetSelection(pos-1)

    def OnButton3Button(self, event):
        """ Edit file """
        app = options.Options().Prefs()['editor']
        file = "%s/%s" % (self.fdir_olay, self.GetOverlaySelection())
        #TODO:
        # This fails if app has switches: "/usr/bin/gvim -f"
        # Also, if they don't put the full path, it'll fail.
        #if not os.path.exists(f):
        #    print "!!! Editor app not found."
        #    return
        if app:
            os.system("%s %s &" % (app, file))

    def OnButton4Button(self, event):
        """ Launch graphical diff """
        app = options.Options().Prefs()['diff']
        file1 = "%s/%s" % (self.fdir, self.GetPortdirSelection())
        file2 = "%s/%s" % (self.fdir_olay, self.GetOverlaySelection())
        #TODO:
        # This fails if app has switches: "/usr/bin/foodiff -f"
        #if not os.path.exists(f):
        #    print "!!! Editor app not found."
        #    return
        if app:
            if os.path.exists(file1):
                if os.path.exists(file2):
                    os.system("%s %s %s&" % (app, file1, file2))


    def OnButton5Button(self, event):
        """ Quit """
        self.Destroy()

    def GetPortdirFiles(self):
        return os.listdir(self.fdir)

    def GetOverlayFiles(self):
        return os.listdir(self.fdir_olay)

    def GetPortdirSelection(self):
        return self.listBox1.GetString(self.listBox1.GetSelection())

    def GetOverlaySelection(self):
        return self.listBox2.GetString(self.listBox2.GetSelection())
