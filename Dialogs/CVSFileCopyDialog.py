"""

Dialog for copying files in PORTDIR_OVERLAY/FILESDIR
to CVSDIR/FILESDIR, or using diff

"""

import os
import shutil

import wx

import options

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON2, 
 wxID_WXFRAME1BUTTON3, wxID_WXFRAME1BUTTON4, wxID_WXFRAME1BUTTON5, 
 wxID_WXFRAME1LISTBOX1, wxID_WXFRAME1LISTBOX2, wxID_WXFRAME1PANEL1, 
 wxID_WXFRAME1STATICBOX1, wxID_WXFRAME1STATICBOX2, wxID_WXFRAME1STATICTEXT1, 
] = map(lambda _init_ctrls: wx.NewId(), range(12))

class wxFrame1(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wx.Point(100, 96), size=wx.Size(754, 439),
              style=wx.DEFAULT_FRAME_STYLE, title='Copy/Diff/Edit in ${FILESDIR}')
        self.SetClientSize(wx.Size(754, 439))

        self.panel1 = wx.Panel(id=wxID_WXFRAME1PANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(754, 439),
              style=wx.TAB_TRAVERSAL)
        self.panel1.SetAutoLayout(True)

        self.staticBox1 = wx.StaticBox(id=wxID_WXFRAME1STATICBOX1,
              label='${FILESDIR} PORTDIR_OVERLAY', name='staticBox1',
              parent=self.panel1, pos=wx.Point(16, 16), size=wx.Size(288, 408),
              style=0)

        self.staticBox2 = wx.StaticBox(id=wxID_WXFRAME1STATICBOX2,
              label='${FILESDIR} in CVS dir', name='staticBox2',
              parent=self.panel1, pos=wx.Point(376, 16), size=wx.Size(360, 408),
              style=0)

        self.button1 = wx.Button(id=wxID_WXFRAME1BUTTON1, label='Copy',
              name='button1', parent=self.panel1, pos=wx.Point(312, 100),
              size=wx.Size(56, 24), style=0)
        wx.EVT_BUTTON(self.button1, wxID_WXFRAME1BUTTON1, self.OnButton1Button)

        self.staticText1 = wx.StaticText(id=wxID_WXFRAME1STATICTEXT1,
              label='--->', name='staticText1', parent=self.panel1,
              pos=wx.Point(328, 80), size=wx.Size(23, 14), style=0)

        self.button2 = wx.Button(id=wxID_WXFRAME1BUTTON2, label='Delete',
              name='button2', parent=self.panel1, pos=wx.Point(672, 192),
              size=wx.Size(56, 24), style=0)
        wx.EVT_BUTTON(self.button2, wxID_WXFRAME1BUTTON2, self.OnButton2Button)

        self.button5 = wx.Button(id=wxID_WXFRAME1BUTTON5, label='Done',
              name='button5', parent=self.panel1, pos=wx.Point(312, 392),
              size=wx.Size(56, 24), style=0)
        wx.EVT_BUTTON(self.button5, wxID_WXFRAME1BUTTON5, self.OnButton5Button)

        self.listBox1 = wx.ListBox(choices=[], id=wxID_WXFRAME1LISTBOX1,
              name='listBox1', parent=self.panel1, pos=wx.Point(24, 40),
              size=wx.Size(272, 376), style=wx.LB_SINGLE)

        self.listBox2 = wx.ListBox(choices=[], id=wxID_WXFRAME1LISTBOX2,
              name='listBox2', parent=self.panel1, pos=wx.Point(384, 40),
              size=wx.Size(280, 376), style=wx.LB_SINGLE)

        self.button3 = wx.Button(id=wxID_WXFRAME1BUTTON3, label='Edit',
              name='button3', parent=self.panel1, pos=wx.Point(672, 240),
              size=wx.Size(56, 24), style=0)
        wx.EVT_BUTTON(self.button3, wxID_WXFRAME1BUTTON3, self.OnButton3Button)

        self.button4 = wx.Button(id=wxID_WXFRAME1BUTTON4, label='Diff',
              name='button4', parent=self.panel1, pos=wx.Point(312, 144),
              size=wx.Size(56, 24), style=0)
        wx.EVT_BUTTON(self.button4, wxID_WXFRAME1BUTTON4, self.OnButton4Button)

    def __init__(self, parent, dir_from, dir_to):
        self._init_ctrls(parent)
        self.dir_from = "%s/files" % dir_from
        self.dir_to = "%s/files" % dir_to

        if not os.path.exists(self.dir_from):
            #Disable widgets if package doesn't exist in CVS FILESDIR
            self.listBox1.Disable()
            self.button1.Disable()
            self.button4.Disable()
            self.staticBox1.Disable()
            self.staticText1.Disable()
        else:
            files = self.GetFromDirFile()
            for f in files:
                self.listBox1.Append(f)

        files = self.GetToDirFile()
        for f in files:
            self.listBox2.Append(f)

    def OnButton1Button(self, event):
        """ Copy file """
        #TODO: If exists, pop up dialog and don't Append to list
        f = self.GetPortdirSelection()
        src = "%s/%s" % (self.dir_from, f)
        dest = "%s/%s" % (self.dir_to, f)
        if os.path.exists(src):
            if os.path.exists(dest):
                dlg = wx.MessageDialog(self, "File already exists in OVERLAY.\n\nOverwrite?", "Error", wx.YES_NO)
                v = dlg.ShowModal()
                if v == wx.ID_YES:
                    shutil.copy(src, dest)
                    return
                else:
                    return
            shutil.copy(src, dest)
            self.listBox2.Append(os.path.basename(src))

    def OnButton2Button(self, event):
        """ Delete file in ${FILESDIR} CVS """
        f = self.GetOverlaySelection()
        pos = self.listBox2.GetSelection()
        victim = "%s/%s" % (self.dir_to, f)
        if os.path.exists(victim):
            #Nothing is selected:
            if os.path.isdir(victim):
                return 
            else:
                msg = "Delete this file?\n\n%s" % victim
                dlg = wx.MessageDialog(self, msg, "Delete file?", wx.YES_NO)
                v = dlg.ShowModal()
                if v == wx.ID_YES:
                    os.remove(victim)
                    self.listBox2.Delete(pos)
                    self.listBox2.SetSelection(pos-1)

    def OnButton3Button(self, event):
        """ Edit file """
        app = options.Options().Prefs()['editor']
        file = "%s/%s" % (self.dir_to, self.GetOverlaySelection())
        #TODO:
        # This fails if app has switches: "/usr/bin/gvim -f"
        # Also, if they don't put the full path, it'll fail.
        #if not os.path.exists(f):
        #    print "!!! Editor app not found."
        #    return
        if os.path.isdir(file):
            return
        if app:
            os.system("%s %s &" % (app, file))

    def OnButton4Button(self, event):
        """ Launch graphical diff """
        app = options.Options().Prefs()['diff']
        file1 = "%s/%s" % (self.dir_from, self.GetPortdirSelection())
        file2 = "%s/%s" % (self.dir_to, self.GetOverlaySelection())
        #TODO:
        # This fails if app has switches: "/usr/bin/foodiff -f"
        #
        #if not os.path.exists(f):
        #    print "!!! app not found."
        #    return
        #
        # We'll try:
        # which app 
        # Or if it starts with '/' check if it exists, minus any flags

        if os.path.isdir(file1) or os.path.isdir(file2):
            return 
        if app:
            if os.path.exists(file1):
                if os.path.exists(file2):
                    os.system("%s %s %s&" % (app, file1, file2))


    def OnButton5Button(self, event):
        """ Quit """
        self.Destroy()

    def GetFromDirFile(self):
        return os.listdir(self.dir_from)

    def GetToDirFile(self):
        return os.listdir(self.dir_to)

    def GetPortdirSelection(self):
        return self.listBox1.GetString(self.listBox1.GetSelection())

    def GetOverlaySelection(self):
        return self.listBox2.GetString(self.listBox2.GetSelection())
