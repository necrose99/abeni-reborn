import os

import wx.html

from options import Options

class MyURILink(wx.html.HtmlWindow):

    """URI widget for homepage in Notes tab"""

    def __init__(self, parent, foo):
        """Initialize html class"""
        wx.html.HtmlWindow.__init__(self, parent, -1)
        self.set_uri()

    def OnLinkClicked(self, linkinfo):
        myOptions = Options()
        p = myOptions.Prefs()
        browser = p['browser']
        if browser:
            os.system("%s %s &" % (browser, linkinfo.GetHref()))
        else:
            print "!!! Error: No web browser set in preferences."

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
                Homepage: 
                </body>
                </html>'''
        self.SetPage(text)
        ir = self.GetInternalRepresentation()
        #self.SetSize( (ir.GetWidth(), ir.GetHeight()) )
