import os

import wx.html

import options

class MyURILink(wx.html.HtmlWindow):

    """URI widget for homepage in Notes tab"""

    def __init__(self, parent, foo):
        """Initialize html class"""
        wx.html.HtmlWindow.__init__(self, parent, -1)
        self.SetStandardFonts()
        self.set_uri()

    def OnLinkClicked(self, linkinfo):
        myOptions = options.Options()
        p = myOptions.Prefs()
        browser = p['browser']
        if browser:
            os.system("%s %s &" % (browser, linkinfo.GetHref()))
        else:
            print "!!! Error: No web browser set in preferences."

    def set_uri(self, uri = "", link_text = "", herds = "", maint = ""):
        """Set URI and render"""
        if uri:
            text = '''<html>
                <body bgcolor="#dddaec">
                <b>Homepage:</b> <a href="%s">%s</a><br>
                <b>Herds:</b> %s<br>
                <b>Maintainers:</b> %s<br>
                </body>
                </html>''' % (uri, link_text, herds, maint)
        else:
            text = '''<html>
                <body bgcolor="#dddaec">
                <b>Homepage:</b><br>
                <b>Herd:</b><br>
                <b>Maintainer info:</b><br>
                </body>
                </html>'''
        self.SetPage(text)
        #ir = self.GetInternalRepresentation()
        #self.SetSize( (ir.GetWidth(), ir.GetHeight()) )
