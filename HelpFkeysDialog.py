import sys

import wx
import wx.html
import wx.lib.wxpTag

import __version__

#---------------------------------------------------------------------------

class MyHelpFkeys(wx.Dialog):
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
<p>
Shift+F1  - clean<br>
F1  - create digest<br>
F2  - unpack<br>
F3  - compile<br>
F4  - install<br>
F5  - qmerge<br> 
F6  - New function<br>
F7  - edit this ebuild in external editor<br>
F8  - ${FILESDIR} dialog: copy from PORTDIR, rm, diff etc.<br>
F9  - ebuild <this ebuild> command<br>
F10 - emerge<br>
F11 - Clear log window<br>
F12 - xterm in ${S}<br>
Shift+F12 - xterm in CVS cat/pn dir<br>
</p>
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
        wx.Dialog.__init__(self, parent, -1, 'Abeni Fkeys',)
        html = wx.html.HtmlWindow(self, -1, size=(420, -1))
        py_version = sys.version.split()[0]
        html.SetPage(self.text % (__version__.version, py_version, wx.VERSION_STRING))
        btn = html.FindWindowById(wx.ID_OK)
        btn.SetDefault()
        ir = html.GetInternalRepresentation()
        html.SetSize( (ir.GetWidth()+25, ir.GetHeight()+25) )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)

