import wx
import utils

class EmergeDialog(wx.Dialog):

    """Dialog box for running emerge with options"""

    def __init__(self, parent, ID, title,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_DIALOG_STYLE):
        provider = wx.SimpleHelpProvider()
        wx.HelpProvider_Set(provider)
        self.parent = parent
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI dialog using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wx.Python extension is concerned.
        self.this = pre.this
        sizer = wx.BoxSizer(wx.VERTICAL)
        box = wx.BoxSizer(wx.HORIZONTAL)

        useLabel = wx.StaticText(self, -1, "USE=")
        useLabel.SetHelpText("Enter any USE variables for the emerge command.")
        box.Add(useLabel, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.use = wx.TextCtrl(self, -1, parent.pref["use"], size=(100,-1))
        self.use.SetHelpText("Enter any USE variables for the emerge command.")
        box.Add(self.use, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        featuresLabel = wx.StaticText(self, -1, "FEATURES=")
        featuresLabel.SetHelpText("Enter any variables for FEATURES.")
        box.Add(featuresLabel, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.features = wx.TextCtrl(self, -1, parent.pref["features"], size=(100,-1))
        self.features.SetHelpText("Enter any variables for FEATURES.")
        box.Add(self.features, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        box = wx.BoxSizer(wx.HORIZONTAL)

        self.cat_pack_ver = utils.get_cpvr(parent)

        cmd = "emerge --oneshot --nospinner =%s"  % self.cat_pack_ver

        pretend_cmd = "emerge --nospinner -pv =%s"  % self.cat_pack_ver

        self.emerge = wx.TextCtrl(self, -1, cmd, size=(560,-1))
        self.emerge.SetHelpText("Enter any options for the emerge command.")
        box.Add(self.emerge, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        box = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        box = wx.BoxSizer(wx.HORIZONTAL)

        btn = wx.Button(self, wx.ID_OK, " Emerge ")
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        wx.ID_PRETEND_EMERGE = wx.NewId()
        btn = wx.Button(self, wx.ID_PRETEND_EMERGE, " Pretend ")
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        wx.EVT_BUTTON(btn, wx.ID_PRETEND_EMERGE, self.OnPretendButton)


        btn = wx.Button(self, wx.ID_CANCEL, " Cancel ")
        btn.SetDefault()
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        btn = wx.ContextHelpButton(self)
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def OnPretendButton(self, event):
        """ emerge -pv this ebuild """
        pretend_cmd = "FEATURES='%s' USE='%s' emerge --nospinner -pv =%s" \
                   % (self.features.GetValue(), self.use.GetValue(), self.cat_pack_ver)
        self.parent.Write(">>> %s" % pretend_cmd)
        self.parent.ExecuteInLog(pretend_cmd)
