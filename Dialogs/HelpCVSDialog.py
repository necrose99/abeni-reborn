import sys

import wx
import wx.html
import wx.lib.wxpTag

import __version__

#---------------------------------------------------------------------------

class MyHelpCVS(wx.Dialog):
    text = '''
<html>
<body bgcolor="#dddaec">
<table bgcolor="#7a5ada" width="100%%" cellspacing="0"
cellpadding="0" border="1">
<tr>
    <td align="center">
    <font color="#ffffff">
    <h2>Abeni %s</h2>
    Python %s<br>
    wxPython %s<br>
    </font">
    </td>
</tr>
</table>
CVS repoman commits have been disabled until gpg signing
of manifests is added in Abeni version ~0.2.0
        <p><wxp module="wx" class="Button">
        <param name="label" value="Okay">
        <param name="id"    value="ID_OK">
        </wxp></p>

</center>
</body>
</html>
'''
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'Help: repoman CVS commits',)
        html = wx.html.HtmlWindow(self, -1, size=(420, -1))
        py_version = sys.version.split()[0]
        html.SetPage(self.text % (__version__.version, py_version, wx.VERSION_STRING))
        btn = html.FindWindowById(wx.ID_OK)
        btn.SetDefault()
        ir = html.GetInternalRepresentation()
        html.SetSize( (ir.GetWidth()+25, ir.GetHeight()+25) )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)

