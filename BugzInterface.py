
'''

This module requires two packages not in portage yet. I've submitted them
to bugs.gentoo.org:
Bug# 27581
Bug# 27582

If you run this module it will create a new bug and upload an
attachment to http://bugs.gentoo.org.

'''

import urllib
import types
import string
import sys
import os

try:
    import ClientForm
    from ClientForm import ControlNotFoundError,  ItemNotFoundError, \
         ItemCountError, ParseError, ParseResponse
    import ClientCookie
except:
    print __doc__
    sys.exit(1)

from urllib2 import urlopen
from cStringIO import StringIO
import options

class HandleForm:
    '''Parses bugs.gentoo.org forms, handles cookies and uploads attachments'''

    def __init__(self, filename, summary, desc, uri, password, user):
        self.filename = filename
        self.ebuild = os.path.basename(filename)
        self.summary = summary
        self.desc = desc
        self.uri = uri
        self.password = password
        self.bugNbr = 0
        self.user = user

    def Login(self):
        url = "http://bugs.gentoo.org/enter_bug.cgi?product=Gentoo%20Linux"
        forms = ParseResponse(ClientCookie.urlopen(url))
        form = forms[0]
        print forms[0]
        try:
            form["Bugzilla_login"] = self.user
            form["Bugzilla_password"] = self.password
            response = ClientCookie.urlopen(form.click("GoAheadAndLogIn"))
        except:
            #Already logged in with coookies
            pass

    def EnterNewBug(self):
        url = "http://bugs.gentoo.org/enter_bug.cgi?product=Gentoo%20Linux"
        forms = ParseResponse(ClientCookie.urlopen(url))
        form = forms[0]
        form["component"] = ["Ebuilds"]
        form["bug_severity"] = ["enhancement"]
        form["bug_file_loc"] = self.uri
        form["short_desc"] = self.summary
        form["comment"] = self.desc
        request = form.click()
        response2 = ClientCookie.urlopen(request)
        lines = response2.read()
        #print response2.info() web server header info

        for l in lines:
            if l.find("Submitted") != -1:
                self.bugNbr = l.split()[1]
                print "Bug number %s created." % self.bugNbr
                break

    def UploadAttachment(self):
        import cgi
        url = "http://bugs.gentoo.org/attachment.cgi?bugid=%s&action=enter" % self.bugNbr
        forms = ParseResponse(ClientCookie.urlopen(url))
        form = forms[0]
        print form
        form["description"] = self.ebuild
        form["contenttypemethod"] = ["list"]
        form["contenttypeselection"] = ["text/plain"]
        form["comment"] = ""
        f = file(self.filename)
        form.add_file(f, "text/plain", self.ebuild)
        request = form.click()
        response2 = ClientCookie.urlopen(request)
        print "Attachment uploaded."
        print response2.read()
        print response2.info()

