import dialog

from wxPython.wx import *

class ChmodWindow (dialog.DialogWindow):

    # User permission IDs
    idCHECK_UREAD  = wxNewId ()
    idCHECK_UWRITE = wxNewId ()
    idCHECK_UEXEC  = wxNewId ()

    # Group permission IDs
    idCHECK_GREAD  = wxNewId ()
    idCHECK_GWRITE = wxNewId ()
    idCHECK_GEXEC  = wxNewId ()

    # Other permission IDs
    idCHECK_OREAD  = wxNewId ()
    idCHECK_OWRITE = wxNewId ()
    idCHECK_OEXEC  = wxNewId ()

    def __init__ (self, parent, file, perm, title=None):
        if __debug__:
            pass
        self.file = file
        self.mode = perm

        if title is None:
            title = "Ftpcube - Change File Permissions"
        dialog.DialogWindow.__init__ (self, parent, title)
        #self.SetIcon (main.getApp ().getAppIcon ())

        panel = self.getDialogPanel ()

        # Construct the user permissions section
        self.uread = wxCheckBox (panel, self.idCHECK_UREAD, "Read")
        self.uwrite = wxCheckBox (panel, self.idCHECK_UWRITE, "Write")
        self.uexec = wxCheckBox (panel, self.idCHECK_UEXEC, "Exec")
        ufsizer = wxGridSizer (1, 3)
        ufsizer.AddMany ([
            (self.uread, 0, wxALIGN_CENTER_HORIZONTAL), (self.uwrite, 0, wxALIGN_CENTER_HORIZONTAL), (self.uexec, 0, wxALIGN_CENTER_HORIZONTAL)
        ])
        ubox = wxStaticBox (panel, -1, "User Access")
        usizer = wxStaticBoxSizer (ubox, wxHORIZONTAL)
        usizer.Add (ufsizer, 1, wxEXPAND)

        # Construct the group permissions section
        self.gread = wxCheckBox (panel, self.idCHECK_GREAD, "Read")
        self.gwrite = wxCheckBox (panel, self.idCHECK_GWRITE, "Write")
        self.gexec = wxCheckBox (panel, self.idCHECK_GEXEC, "Exec")
        gfsizer = wxGridSizer (1, 3)
        gfsizer.AddMany ([
            (self.gread, 0, wxALIGN_CENTER_HORIZONTAL), (self.gwrite, 0, wxALIGN_CENTER_HORIZONTAL), (self.gexec, 0, wxALIGN_CENTER_HORIZONTAL)
        ])
        gbox = wxStaticBox (panel, -1, "Group Access")
        gsizer = wxStaticBoxSizer (gbox, wxHORIZONTAL)
        gsizer.Add (gfsizer, 1, wxEXPAND)

        # Construct the others permissions section
        self.oread = wxCheckBox (panel, self.idCHECK_OREAD, "Read")
        self.owrite = wxCheckBox (panel, self.idCHECK_OWRITE, "Write")
        self.oexec = wxCheckBox (panel, self.idCHECK_OEXEC, "Exec")
        ofsizer = wxGridSizer (1, 3)
        ofsizer.AddMany ([
            (self.oread, 0, wxALIGN_CENTER_HORIZONTAL), (self.owrite, 0, wxALIGN_CENTER_HORIZONTAL), (self.oexec, 0, wxALIGN_CENTER_HORIZONTAL)
        ])
        obox = wxStaticBox (panel, -1, "Other Access")
        osizer = wxStaticBoxSizer (obox, wxHORIZONTAL)
        osizer.Add (ofsizer, 1, wxEXPAND)

        file_label = wxStaticText (panel, -1, "Permissions for: %(file)s"
                                              %{ 'file' : self.file })

        fsizer = wxFlexGridSizer (7, 3)
        fsizer.AddMany ([
            (10, 10), (10, 10), (10, 10),
            (10, 5), (usizer, 1, wxEXPAND), (10, 5),
            (10, 10), (10, 10), (10, 10),
            (10, 5), (gsizer, 1, wxEXPAND), (10, 5),
            (10, 10), (10, 5), (10, 5),
            (10, 5), (osizer, 1, wxEXPAND), (10, 5),
            (10, 10), (10, 10), (10, 10),
            (10, 5), (file_label, 0, wxALIGN_CENTER_HORIZONTAL), (10, 5),
        ])
        fsizer.AddGrowableCol (1)

        sizer = wxFlexGridSizer (3, 3)
        sizer.AddMany ([
            (10, 10), (10, 10), (10, 10),
            (10, 10), (fsizer, 1, wxEXPAND), (10, 10),
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
            print "Ack! Attempted to display invalid permissions in chmod dialog"
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
