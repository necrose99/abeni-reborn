import os

import wx.html

class MyURILink(wx.html.HtmlWindow):

    """URI widget for homepage in Notes tab"""

    def __init__(self, parent, foo):
        """Initialize html class"""
        wx.html.HtmlWindow.__init__(self, parent, -1)
        self.set_uri()

    def OnLinkClicked(self, linkinfo):
        print linkinfo.GetHref()
        os.system("firefox %s &" % linkinfo.GetHref())

    def set_uri(self, uri="", link_text=""):
        """Set URI and render"""
        if uri:
            text = '''<html>
                <body bgcolor="#dddaec">
                Homepage: <a href="%s">%s</a>
                </body>
                </html>''' % (uri, link_text)
        else:
            text = '''<html>
                <body bgcolor="#dddaec">
                Homepage: (Not set)
                </body>
                </html>'''
        self.SetPage(text)
        ir = self.GetInternalRepresentation()
        #self.SetSize( (ir.GetWidth(), ir.GetHeight()) )
