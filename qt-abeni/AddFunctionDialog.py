#Boa:Dialog:AddFunction

import wx

#TODO: Use wxglade to create this because Boa Constructor
#      doesn't support wxPython 2.5* yet

def create(parent):
    return AddFunction(parent)

[wxID_ADDFUNCTION, wxID_ADDFUNCTIONCANCELBUTTON, 
 wxID_ADDFUNCTIONDEFAULTTEXTCTRL, wxID_ADDFUNCTIONFUNCTIONLISTBOX, 
 wxID_ADDFUNCTIONHELPTEXTCTRL, wxID_ADDFUNCTIONNEWTEXTCTRL, 
 wxID_ADDFUNCTIONOKBUTTON, wxID_ADDFUNCTIONPANEL1, 
 wxID_ADDFUNCTIONSTATICTEXT1, wxID_ADDFUNCTIONSTATICTEXT2, 
 wxID_ADDFUNCTIONSTATICTEXT3, wxID_ADDFUNCTIONSTATICTEXT4, 
] = map(lambda _init_ctrls: wx.NewId(), range(12))

class AddFunction(wx.Dialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_ADDFUNCTION, name='AddFunction',
              parent=prnt, pos=wx.Point(209, 210), size=wx.Size(533, 333),
              style=wx.DEFAULT_DIALOG_STYLE, title='Add Function')
        self._init_utils()
        self.SetClientSize(wx.Size(533, 333))

        self.panel1 = wx.Panel(id=wxID_ADDFUNCTIONPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(533, 333),
              style=wx.TAB_TRAVERSAL)
        self.panel1.SetAutoLayout(True)

        self.functionListBox = wx.ListBox(choices=[],
              id=wxID_ADDFUNCTIONFUNCTIONLISTBOX, name='functionListBox',
              parent=self.panel1, pos=wx.Point(8, 32), size=wx.Size(184, 224),
              style=0, validator=wx.DefaultValidator)
        wx.EVT_LISTBOX(self.functionListBox, wxID_ADDFUNCTIONFUNCTIONLISTBOX,
              self.OnListbox)
        wx.EVT_LISTBOX_DCLICK(self.functionListBox,
              wxID_ADDFUNCTIONFUNCTIONLISTBOX, self.OnOkButton)

        self.staticText1 = wx.StaticText(id=wxID_ADDFUNCTIONSTATICTEXT1,
              label='Standard Functions', name='staticText1',
              parent=self.panel1, pos=wx.Point(8, 8), size=wx.Size(109, 16),
              style=0)

        self.defaultTextCtrl = wx.TextCtrl(id=wxID_ADDFUNCTIONDEFAULTTEXTCTRL,
              name='defaultTextCtrl', parent=self.panel1, pos=wx.Point(208, 152),
              size=wx.Size(312, 128), style=wx.TE_READONLY | wx.TE_MULTILINE,
              value='')

        self.okButton = wx.Button(id=wxID_ADDFUNCTIONOKBUTTON, label='OK',
              name='okButton', parent=self.panel1, pos=wx.Point(216, 296),
              size=wx.Size(80, 22), style=0)
        wx.EVT_BUTTON(self.okButton, wxID_ADDFUNCTIONOKBUTTON, self.OnOkButton)

        self.cancelButton = wx.Button(id=wxID_ADDFUNCTIONCANCELBUTTON,
              label='Cancel', name='cancelButton', parent=self.panel1,
              pos=wx.Point(328, 296), size=wx.Size(80, 22), style=0)
        wx.EVT_BUTTON(self.cancelButton, wxID_ADDFUNCTIONCANCELBUTTON,
              self.OnCancelButton)

        self.staticText2 = wx.StaticText(id=wxID_ADDFUNCTIONSTATICTEXT2,
              label='Help', name='staticText2', parent=self.panel1,
              pos=wx.Point(208, 8), size=wx.Size(26, 16), style=0)

        self.staticText3 = wx.StaticText(id=wxID_ADDFUNCTIONSTATICTEXT3,
              label='Default Contents', name='staticText3', parent=self.panel1,
              pos=wx.Point(208, 130), size=wx.Size(92, 16), style=0)

        self.helpTextCtrl = wx.TextCtrl(id=wxID_ADDFUNCTIONHELPTEXTCTRL,
              name='helpTextCtrl', parent=self.panel1, pos=wx.Point(208, 32),
              size=wx.Size(312, 80), style=wx.TE_READONLY | wx.TE_MULTILINE,
              value='')

        self.staticText4 = wx.StaticText(id=wxID_ADDFUNCTIONSTATICTEXT4,
              label='New, Empty Function', name='staticText4',
              parent=self.panel1, pos=wx.Point(8, 264), size=wx.Size(120, 16),
              style=0)

        self.newTextCtrl = wx.TextCtrl(id=wxID_ADDFUNCTIONNEWTEXTCTRL,
              name='newTextCtrl', parent=self.panel1, pos=wx.Point(8, 288),
              size=wx.Size(184, 32), style=0, value='')
        wx.EVT_TEXT(self.newTextCtrl, wxID_ADDFUNCTIONNEWTEXTCTRL, self.OnText)

    def __init__(self, parent):
        self._init_ctrls(parent)
        
        # self.functions[][0] is the function name
        # self.functions[][1] is the default contents, '' is filled in later.
        # self.functions[][2] is the help
        self.functions = [ 
                ('pkg_setup', '{\n\t\n\t\n\t\n}', 'Use this function to perform any miscellaneous prerequisite tasks. This might include adding system accounts or checking for an existing configuration file.'),
                ('pkg_nofetch', '{\n\teinfo "Please download $A from"\n\teinfo "${SRC_URI}"\n\teinfo "and put into ${DISTFILES}"\n}', 'Inform the user about required actions if for some reason (such as licensing issues) the sources may not be downloaded by Portage automatically. Use this in conjunction with RESTRICT="fetch". You only should display messages in this function, never call "die".'),
                ('src_unpack', '{\n\tunpack ${A} || die "Unpacking the source failed"\n\tcd ${S} || die "Could not change directory."\n}', 'Use this function to unpack your sources, apply patches, and run auxiliary programs such as the autotools. By default, this function unpacks the packages listed in ${A}. The initial working directory is defined by ${WORKDIR}.'),
                ('src_compile (configure/make)', '{\n\teconf || die "Configure failed"\n\temake || die "Make failed"\n}', 'Use this function to configure and build the package. The initial working directory is ${S}.'),
                ('src_install (make install)', '{\n\teinstall || die "Install failed"\n}', 'Use this function install the package to an image in ${D}. If your package uses automake, you can do this simply with "make DESTDIR=${D} install". Make sure your package installs all its files using ${D} as the root! The initial working directory is ${S}.'),
                ('src_install (python)', '{\n\tpython setup.py install --root=${D} --prefix=/usr || die\n}\n', 'Use this function to install a python package to an image in ${D}.  Make sure your package installs all its files using ${D} as the root! The initial working directory is ${S}.'),
                ('pkg_preinst', '{\n\t\n\t\n\t\n}', 'The commands in this function are run just prior to merging a package image into the file system.'),
                ('pkg_postinst', '{\n\teinfo " "\n\t\n}', 'The commands in this function are run just following merging a package image into the file system.'),
                ('pkg_prerm', '{\n\t\n\t\n\t\n}', 'The commands in this function are run just prior to unmerging a package image from the file system.'),
                ('pkg_postrm', '{\n\t\n\t\n\t\n}', 'The commands in this function are run just following unmerging a package image from the file system.'),
                ('pkg_config', '{\n\t\n\t\n\t\n}', 'You use this function to setup an initial configuration for the package after it is installed. All paths in this function should be prefixed with ROOT. This function is only executed if the user runs: "ebuild /var/db/pkg/${CATEGORY}/${PF}/${PF}.ebuild config".')
            ]
        
        # Create self.func_list to give to the ListBox        
        self.func_list = map(lambda x:x[0], self.functions)
        self.functionListBox.Set(self.func_list)
        
        # The self.flag variable is used to identify whether to use
        # the ListBox or the TextCtrl
        self.flag = 1

    def OnListbox(self, event):
        event.Skip()
        selected = self.functions[self.functionListBox.GetSelection()]
        self.helpTextCtrl.SetValue(selected[2])
        self.defaultTextCtrl.SetValue(selected[1])
        
        # If previous input was in TextCtrl, clear the TextCtrl now
        # that a choice has been made in the ListBox
        if not self.flag:
            self.newTextCtrl.Clear()
        self.flag = 1

    def OnOkButton(self, event):
        event.Skip()
        if self.flag:
            selected = self.functions[self.functionListBox.GetSelection()]
        else:
            selected = (self.newTextCtrl.GetValue(), '{\n\t\n\t\n\t\n}', '')
        function_contents = selected[1]
        if not function_contents:
            function_contents = '{\n\t\n\t\n\t\n}'
        self.func = selected[0].split()[0] + '() '
        self.val = self.func + function_contents
        self.EndModal(wx.ID_OK)

    def OnCancelButton(self, event):
        event.Skip()
        self.Close()

    def OnText(self, event):
        event.Skip()
        
        # If starting to type in TextCtrl, clear selection in ListBox
        if self.flag:
            self.functionListBox.SetSelection(self.functionListBox.GetSelection(), select=FALSE)
        self.flag = 0

    def GetFunc(self):
        """Returns function name and function body"""
        return self.func, self.val

