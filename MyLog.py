
from wxPython.wx import *

import utils

class LogWindow(wxFrame):
    """Separate window for log"""
    def __init__(self, parent):
        wxFrame.__init__(self, parent, -1, "Abeni Log", size=wxSize(900, 450))
        self.parent=parent
        self.AddToolbar()
        EVT_CLOSE(self, self.OnClose)
        self.splitter = wxSplitterWindow(self, -1, style=wxNO_3D|wxSP_3D)
        self.parent.text_ctrl_log.Reparent(self.splitter)
        self.scrollLog = wxTextCtrl(self.splitter, -1, style = wxTE_MULTILINE|wxTE_READONLY)
        #TODO: I forget why I did this. Is it necessary?
        def EmptyHandler(evt): pass
        EVT_ERASE_BACKGROUND(self.splitter, EmptyHandler)
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
        self.tb = self.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
        self.ScrollID = wxNewId()
        ScrollBmp = ('/usr/share/pixmaps/abeni/split.png')
        self.tb.AddSimpleTool(self.ScrollID, wxBitmap(ScrollBmp, wxBITMAP_TYPE_PNG), \
                                "Scrollback in split window")
        EVT_TOOL(self, self.ScrollID, self.ScrollBack)

        self.UnsplitID = wxNewId()
        UnsplitBmp = ('/usr/share/pixmaps/abeni/unsplit.png')
        self.tb.AddSimpleTool(self.UnsplitID, wxBitmap(UnsplitBmp, wxBITMAP_TYPE_PNG), \
                                "Un-split window")
        EVT_TOOL(self, self.UnsplitID, self.Unsplit)

        self.CloseID = wxNewId()
        CloseBmp = ('/usr/share/pixmaps/abeni/close_scrollback.png')
        self.tb.AddSimpleTool(self.CloseID, wxBitmap(CloseBmp, wxBITMAP_TYPE_PNG), \
                                "Close this log window")
        EVT_TOOL(self, self.CloseID, self.OnClose)
        self.tb.Realize()

    def ScrollBack(self, event):
        self.scrollLog.SetValue(self.parent.text_ctrl_log.GetValue())
        self.splitter.SetSashPosition(250)

    def Unsplit(self, event):
        self.splitter.SetSashPosition(1)

