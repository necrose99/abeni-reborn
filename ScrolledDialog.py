import os

import wx
from wx.lib.dialogs import ScrolledMessageDialog


class MyScrolledDialog:

    """Eventually sub-class ScrolledMessageDialog and detect unicode"""

    def __init__(self, parent, filename, title):
        """initialize class"""
        self.display_file(parent, filename, title)

    def display_file(self, parent, filename, title):
        """Display txt of filename. If unicode, display GLEP 31 err msg"""
        #TODO: Replace unicode with sane text instead of bombing
        # or possible used StyledTxtCtrl
        if os.path.exists(filename):
                txt = open(filename, 'r').read()
                try:
                    txt = txt.encode("utf8", "replace")
                except UnicodeDecodeError, msg:
                    #Send to stdout since widget can't display:
                    print txt
                    txt = "Error in file %s\n" % filename
                    txt = "%sPossible GLEP 31 violation:\n%s" % (txt, msg)
                    txt = "\n%sCheck stdout for text." % txt

                dlg = ScrolledMessageDialog(parent, txt, title)
                dlg.ShowModal()
        else:
            icon = wx.ICON_ERROR
            msg = "Error - File does not exist:\n%s" % filename
            dlg = wx.MessageDialog(parent, msg, title, wx.OK | icon)
            dlg.ShowModal()
            dlg.Destroy()


