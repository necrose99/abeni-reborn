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
    <h1>Abeni %s</h1>
    Python %s<br>
    wxPython %s<br>
    </font">
    </td>
</tr>
</table>

Official Gentoo developers can use the CVS menu in Abeni to
do repoman commits. It will do the following:<br>
<br>
<ul>
<li>cvs update</li>
<li>copy the build to the CVS dir</li>
<li>prompt you if there are patches etc. in $FILEDIR to copy</li>
<li>create a digest</li>
<li>give a metadata.xml dialog if there is none present</li>
<li>give a dialog for Changelog/commit msgs</li>
<li>repoman full</li>
<li>repoman --pretend commit</li>
<li>ask if you want to actually commit</li>
</ul>

<h2>NOTE:</h2>

Abeni's repoman commit won't work if you use your
CVS directory as your PORTDIR. A future version of Abeni 
will be able to handle that situation. I've never
used CVS as my PORTDIR so haven't tested it. If any
developer would like to try it out, please let me know
how it goes and if special steps are needed.
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

