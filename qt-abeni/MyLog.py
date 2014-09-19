
import wx

import utils

class LogWindow(wx.Frame):
    """Separate window for log"""
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Abeni Log", size=wx.Size(900, 450))
        self.parent=parent
        self.AddToolbar()
        wx.EVT_CLOSE(self, self.OnClose)
        self.splitter = wx.SplitterWindow(self, -1, style=wx.NO_3D|wx.SP_3D)
        self.parent.text_ctrl_log.Reparent(self.splitter)
        self.scrollLog = wx.TextCtrl(self.splitter, -1, style = wx.TE_MULTILINE|wx.TE_READONLY)
        #TODO: I forget why I did this. Is it necessary?
        def EmptyHandler(evt): pass
        wx.EVT_ERASE_BACKGROUND(self.splitter, EmptyHandler)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.splitter.SplitHorizontally(self.scrollLog, self.parent.text_ctrl_log, 1)
        self.splitter.SetMinimumPaneSize(1)
        self.Show(True)

    def OnClose(self, event):
        utils.LogBottom(self.parent, self.parent.text_ctrl_log)
        self.Destroy()

    def AddToolbar(self):
        #Create Toolbar with icons
        # icons are  28 pixels high, variable width
        self.tb = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER|wx.TB_FLAT)
        self.ScrollID = wx.NewId()
        ScrollBmp = ('/usr/share/pixmaps/abeni/split.png')
        self.tb.AddSimpleTool(self.ScrollID, wx.Bitmap(ScrollBmp, wx.BITMAP_TYPE_PNG), \
                                "Scrollback in split window")
        wx.EVT_TOOL(self, self.ScrollID, self.ScrollBack)

        self.UnsplitID = wx.NewId()
        UnsplitBmp = ('/usr/share/pixmaps/abeni/unsplit.png')
        self.tb.AddSimpleTool(self.UnsplitID, wx.Bitmap(UnsplitBmp, wx.BITMAP_TYPE_PNG), \
                                "Un-split window")
        wx.EVT_TOOL(self, self.UnsplitID, self.Unsplit)

        self.CloseID = wx.NewId()
        CloseBmp = ('/usr/share/pixmaps/abeni/close_scrollback.png')
        self.tb.AddSimpleTool(self.CloseID, wx.Bitmap(CloseBmp, wx.BITMAP_TYPE_PNG), \
                                "Close this log window")
        wx.EVT_TOOL(self, self.CloseID, self.OnClose)
        self.tb.Realize()

    def ScrollBack(self, event):
        self.scrollLog.SetValue(self.parent.text_ctrl_log.GetValue())
        self.splitter.SetSashPosition(250)

    def Unsplit(self, event):
        self.splitter.SetSashPosition(1)

