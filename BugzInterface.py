import urllib
import types
import string
import ClientForm
from ClientForm import ControlNotFoundError,  ItemNotFoundError, \
     ItemCountError, ParseError, ParseResponse
from urllib2 import urlopen
import ClientCookie
from cStringIO import StringIO

'''

This requires two packages not in portage yet. I've submitted them
to bugs.gentoo.org:
Bug# 27581
Bug# 27582

If you run this module it will create a new bug and upload an
attachment. It connects to the bugzilla on my computer (Rob's),
NOT bugs.gentoo.org. It hasn't been tested with bugs.gentoo.org
but should work with very little modification.

Feel free to try it out. The only thing you need to change is
self.filename. Just set it to a file you want to upload. Its
set to only upload text/plain. (My computer isn't always online).

'''


class HandleForm:
    '''Parses bugs.gentoo.org forms, handles cookies and uploads attachments'''

    def __init__(self):
        self.filename = "/home/rob/all.txt"

    def Login(self, user="genone@127.0.0.1", password="mauch"):
        url = "http://abeni.kicks-ass.net/bugzilla/enter_bug.cgi"
        forms = ParseResponse(ClientCookie.urlopen(url))
        form = forms[0]
        #print forms[0]
        form["Bugzilla_login"] = "genone@127.0.0.1"
        form["Bugzilla_password"] = "mauch"
        response = ClientCookie.urlopen(form.click("GoAheadAndLogIn"))

    def urlencode_data(self, Dict):
        pairs = []
        for (name, values) in Dict.items():
            ename = urllib.quote(str(name))
            if type(values) != types.ListType:
                values = [values]
            for value in values:
                evalue = urllib.quote(str(value))
                pairs.append( "%s=%s" % (ename, evalue) )
        p = string.joinfields(pairs, "&")
        return p

    def urlpost(self, url, postdata={}):
        uf = urllib.urlopen(url, self.urlencode_data(postdata))
        results = uf.read()
        uf.close()
        return(results)

    def EnterNewBug(self):
        url = "http://abeni.kicks-ass.net/bugzilla/post_bug.cgi"
        data ={
            "GoAheadAndLogin":"1",
            "Bugzilla_login":"genone@127.0.0.1",
            "Bugzilla_password":"mauch",
            "product":"Abeni",
            "version":"0.0.9",
            "component":"GUI",
            "rep_platform":"PC",
            "op_sys":"Linux",
            "priority":"P2",
            "bug_severity":"enhancement",
            "bug_status":"NEW",
            "assigned_to":"genone@127.0.0.1",
            "cc":"",
            "bug_file_loc":"http://",
            "short_desc":"fake-0.1.ebuild (New version)",
            "comment":"This package is a package.",
            "keywords":"",
            "form_name":"enter_bug",
        }
        res = self.urlpost(url, data)
        lines = res.split("\n")
        for l in lines:
            if l.find("Submitted") != -1:
                self.bugNbr = l.split()[1]
                print "Bug number %s created." % self.bugNbr
                break


    def UploadAttachment(self):
        import cgi
        url = "http://abeni.kicks-ass.net/bugzilla/attachment.cgi?bugid=%s&action=enter" % self.bugNbr
        forms = ParseResponse(ClientCookie.urlopen(url))
        form = forms[0]
        #print form
        form["description"] = "fake-0.1.ebuild"
        form["contenttypemethod"] = ["list"]
        form["contenttypeselection"] = ["text/plain"]
        form["comment"] = "my comment"
        f = file(self.filename)  # use StringIO if you have a string to upload
        form.add_file(f, "text/plain", "all.txt")
        request = form.click()
        response2 = ClientCookie.urlopen(request)
        print "Attachment uploaded."
        #print response2.read()
        #print response2.info()

a = HandleForm()
a.Login()
a.EnterNewBug()
a.UploadAttachment()


