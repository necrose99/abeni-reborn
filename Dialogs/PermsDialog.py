
import wx

class DialogWindow(wx.Dialog):

	def __init__ (self, parent, title):
		wx.Dialog.__init__ (self, parent, -1, title)

		self.dialog_panel = wx.Panel (self, -1, style=wx.SUNKEN_BORDER)

	def renderDialog (self):
		ok_button = wx.Button (self, wx.ID_OK, _("Ok"))
		ok_button.SetDefault ()
		cancel_button = wx.Button (self, wx.ID_CANCEL, _("Cancel"))
		bsizer = wx.BoxSizer (wx.HORIZONTAL)
		bsizer.Add (5, 5, 1, wx.EXPAND)
		bsizer.Add (ok_button, 0, wx.EXPAND)
		bsizer.Add (75, 5, 0, wx.EXPAND)
		bsizer.Add (cancel_button, 0, wx.EXPAND)
		bsizer.Add (5, 5, 1, wx.EXPAND)

		sizer = wx.BoxSizer (wx.VERTICAL)
		sizer.Add (self.dialog_panel, 1, wx.EXPAND)
		sizer.Add (15, 15, 0, wx.EXPAND)
		sizer.Add (bsizer, 0, wx.EXPAND)
		sizer.Add (15, 15, 0, wx.EXPAND)
		self.SetAutoLayout (true)
		self.SetSizer (sizer)
		sizer.Fit (self)
		sizer.SetSizeHints (self)

		self.Centre ()

	def getDialogPanel (self):
		return self.dialog_panel


class ChmodWindow (DialogWindow):

    """Dialog for changing file permissions"""

    # User permission IDs
    idCHECK_UREAD  = wx.NewId ()
    idCHECK_UWRITE = wx.NewId ()
    idCHECK_UEXEC  = wx.NewId ()

    # Group permission IDs
    idCHECK_GREAD  = wx.NewId ()
    idCHECK_GWRITE = wx.NewId ()
    idCHECK_GEXEC  = wx.NewId ()

    # Other permission IDs
    idCHECK_OREAD  = wx.NewId ()
    idCHECK_OWRITE = wx.NewId ()
    idCHECK_OEXEC  = wx.NewId ()

    def __init__ (self, parent, file, perm, title=None):
        if __debug__:
            pass
        self.file = file
        self.mode = perm

        if title is None:
            title = "Change File Permissions"
        DialogWindow.__init__ (self, parent, title)

        panel = self.getDialogPanel ()

        self.uread = wx.CheckBox (panel, self.idCHECK_UREAD, "Read")
        self.uwrite = wx.CheckBox (panel, self.idCHECK_UWRITE, "Write")
        self.uexec = wx.CheckBox (panel, self.idCHECK_UEXEC, "Exec")
        ufsizer = wx.GridSizer (1, 3)
        ufsizer.AddMany ([
            (self.uread, 0, wx.ALIGN_CENTER_HORIZONTAL), (self.uwrite, 0, wx.ALIGN_CENTER_HORIZONTAL), (self.uexec, 0, wx.ALIGN_CENTER_HORIZONTAL)
        ])
        ubox = wx.StaticBox (panel, -1, "User Access")
        usizer = wx.StaticBoxSizer (ubox, wx.HORIZONTAL)
        usizer.Add (ufsizer, 1, wx.EXPAND)

        self.gread = wx.CheckBox (panel, self.idCHECK_GREAD, "Read")
        self.gwrite = wx.CheckBox (panel, self.idCHECK_GWRITE, "Write")
        self.gexec = wx.CheckBox (panel, self.idCHECK_GEXEC, "Exec")
        gfsizer = wx.GridSizer (1, 3)
        gfsizer.AddMany ([
            (self.gread, 0, wx.ALIGN_CENTER_HORIZONTAL), (self.gwrite, 0, wx.ALIGN_CENTER_HORIZONTAL), (self.gexec, 0, wx.ALIGN_CENTER_HORIZONTAL)
        ])
        gbox = wx.StaticBox (panel, -1, "Group Access")
        gsizer = wx.StaticBoxSizer (gbox, wx.HORIZONTAL)
        gsizer.Add (gfsizer, 1, wx.EXPAND)

        self.oread = wx.CheckBox (panel, self.idCHECK_OREAD, "Read")
        self.owrite = wx.CheckBox (panel, self.idCHECK_OWRITE, "Write")
        self.oexec = wx.CheckBox (panel, self.idCHECK_OEXEC, "Exec")
        ofsizer = wx.GridSizer (1, 3)
        ofsizer.AddMany ([
            (self.oread, 0, wx.ALIGN_CENTER_HORIZONTAL), (self.owrite, 0, wx.ALIGN_CENTER_HORIZONTAL), (self.oexec, 0, wx.ALIGN_CENTER_HORIZONTAL)
        ])
        obox = wx.StaticBox (panel, -1, "Other Access")
        osizer = wx.StaticBoxSizer (obox, wx.HORIZONTAL)
        osizer.Add (ofsizer, 1, wx.EXPAND)

        file_label = wx.StaticText (panel, -1, "Permissions for: %(file)s"
                                              %{ 'file' : self.file })

        fsizer = wx.FlexGridSizer (7, 3)
        fsizer.AddMany ([
            (10, 10), (10, 10), (10, 10),
            (10, 5), (usizer, 1, wx.EXPAND), (10, 5),
            (10, 10), (10, 10), (10, 10),
            (10, 5), (gsizer, 1, wx.EXPAND), (10, 5),
            (10, 10), (10, 5), (10, 5),
            (10, 5), (osizer, 1, wx.EXPAND), (10, 5),
            (10, 10), (10, 10), (10, 10),
            (10, 5), (file_label, 0, wx.ALIGN_CENTER_HORIZONTAL), (10, 5),
        ])
        fsizer.AddGrowableCol (1)

        sizer = wx.FlexGridSizer (3, 3)
        sizer.AddMany ([
            (10, 10), (10, 10), (10, 10),
            (10, 10), (fsizer, 1, wx.EXPAND), (10, 10),
            (10, 10), (10, 10), (10, 10)
        ])
        sizer.AddGrowableCol (1)
        sizer.AddGrowableRow (1)

        panel.SetAutoLayout (true)
        panel.SetSizer (sizer)
        sizer.Fit (panel)
        sizer.SetSizeHints (panel)

        try:
            self.displayPermissions ()
        except TypeError:
            print "!!! Attempted to display invalid permissions in chmod dialog"
            self.Destroy ()
            return

        self.SetSizeHints (300, -1)
        self.renderDialog ()

    def getFile (self):
        return self.file

    def getPermissions (self):
        if self.mode is None:
            return self.mode

        # Build the permissions via the checkbox values
        perm = 0
        if self.uread.GetValue ():
            perm |= (4 << 6)
        if self.uwrite.GetValue ():
            perm |= (2 << 6)
        if self.uexec.GetValue ():
            perm |= (1 << 6)
        if self.gread.GetValue ():
            perm |= (4 << 3)
        if self.gwrite.GetValue ():
            perm |= (2 << 3)
        if self.gexec.GetValue ():
            perm |= (1 << 3)
        if self.oread.GetValue ():
            perm |= 4
        if self.owrite.GetValue ():
            perm |= 2
        if self.oexec.GetValue ():
            perm |= 1
        return perm

    def displayPermissions (self):
        if not isinstance (self.mode, int):
            raise TypeError, "permission must be an int"

        # Extract the permissions and set the check boxs accordingly
        if self.mode & (4 << 6):
            self.uread.SetValue (true)
        if self.mode & (2 << 6):
            self.uwrite.SetValue (true)
        if self.mode & (1 << 6):
            self.uexec.SetValue (true)
        if self.mode & (4 << 3):
            self.gread.SetValue (true)
        if self.mode & (2 << 3):
            self.gwrite.SetValue (true)
        if self.mode & (1 << 3):
            self.gexec.SetValue (true)
        if self.mode & 4:
            self.oread.SetValue (true)
        if self.mode & 2:
            self.owrite.SetValue (true)
        if self.mode & 1:
            self.oexec.SetValue (true)


