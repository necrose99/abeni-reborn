"""AboutDialog.py

Obligatory about dialog

"""

import sys

import wx 
import wx.html
import wx.lib.wxpTag

import __version__


class MyAboutBox(wx.Dialog):

    """HTML window for about dialog"""

    text = """<html>
        <body bgcolor="#dddaec">
        <center><table bgcolor="#7a5ada" width="100%%" cellspacing="0"
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

        <p><b>Abeni</b> is an IDE for creating ebuilds for
        Gentoo Linux</p>
        <br>
        <img src="/usr/share/pixmaps/abeni/gentoo-logo.png">
        <br>
        <p><b>Abeni</b> was written by<br>
        <b>Rob Cakebread - pythonhead@gentoo.org</b><br><br>
        with contributions from:<br><br>
        <b>Marius Mauch - genone@gentoo.org<br>
        Tim Cera - timcera@earthlink.net</b><br><br>
        <b>Abeni</b> is Copyright (c) 2003-2004
        <b>Rob Cakebread</b> <pythonhead@gentoo.org>.</p>
        <p>
        <font size="-1"><b>Abeni</b> is released under the terms of<br>
        the GNU Public License v.2</font>
        </p>
        <p>
        Abeni is <i>not</i> an official Gentoo product.
        </p>
        <p><wxp module="wx" class="Button">
        <param name="label" value="Okay">
        <param name="id"    value="ID_OK">
        </wxp></p>
        </center>
        </body>
        </html>
        """

    def __init__(self, parent):
        """Setup html widget"""
        wx.Dialog.__init__(self, parent, -1, 'About Abeni',)
        html = wx.html.HtmlWindow(self, -1, size=(420, -1))
        py_version = sys.version.split()[0]
        html.SetPage(self.text % (__version__.version, py_version, wx.VERSION_STRING))
        btn = html.FindWindowById(wx.ID_OK)
        btn.SetDefault()
        ir = html.GetInternalRepresentation()
        html.SetSize( (ir.GetWidth()+25, ir.GetHeight()+25) )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)

