import sys

import wx   # About module uses the new wx namespace
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
    <h1>Abeni %s</h1>
    Python %s<br>
    wxPython %s<br>
    </font">
    </td>
</tr>
</table>

Official Gentoo developers can use the CVS menu in Abeni to
do repoman commits. It will do a <b>cvs update</b>, copy the build
and files needed from $FILESDIR to your CVS dir, create a digest,
give a dialog for Changelog/commit msgs, do a 
<b>repoman full</b>, <b>repoman --pretend commit</b>
and then ask if you want to actually commit.

<h2>NOTE:</h2>

Abeni's repoman commit will only work if you don't use your
CVS directory as your PORTDIR. The next version of Abeni will
be able to handle that situation.
<center>
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

