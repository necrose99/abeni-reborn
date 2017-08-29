#!/usr/bin/env python
# -*- coding: ANSI_X3.4-1968 -*-
#
# generated by wxGlade HG on Sat May 24 09:06:30 2014
#

import wx

<1401423105813442059wxGlade replace dependencies>
# begin wxGlade: extracode
# end wxGlade


class GetURIDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: GetURIDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_uri = wx.StaticText(self, -1, _("Package URI:"))
        self.URI = wx.TextCtrl(self, -1, "")
        self.label_template = wx.StaticText(self, -1, _("Template:"))
        self.combo_box_1 = wx.ComboBox(self, -1, choices=[], style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
        self.static_line_2 = wx.StaticLine(self, -1)
        self.button_cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        self.button_ok = wx.Button(self, wx.ID_OK, "")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: GetURIDialog.__set_properties
        self.SetTitle(_("Enter URI for package"))
        self.SetSize((407, 146))
        self.URI.SetMinSize((304, 22))
        self.button_ok.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: GetURIDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.label_uri, 0, wx.LEFT, 4)
        sizer_2.Add(self.URI, 1, wx.LEFT, 12)
        sizer_1.Add(sizer_2, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 10)
        sizer_3.Add(self.label_template, 0, wx.LEFT|wx.ALIGN_RIGHT, 4)
        sizer_3.Add(self.combo_box_1, 1, wx.LEFT, 20)
        sizer_1.Add(sizer_3, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 10)
        sizer_1.Add(self.static_line_2, 0, wx.EXPAND, 0)
        sizer_4.Add(self.button_cancel, 0, 0, 0)
        sizer_4.Add((20, 20), 0, 0, 0)
        sizer_4.Add(self.button_ok, 0, 0, 0)
        sizer_1.Add(sizer_4, 0, wx.ALL|wx.EXPAND, 12)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

# end of class GetURIDialog
if __name__ == "__main__":
    gettext.install("app") # replace with the appropriate catalog name

    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    dialog_1 = GetURIDialog(None, wx.ID_ANY, "")
    app.SetTopWindow(dialog_1)
    dialog_1.Show()
    app.MainLoop()