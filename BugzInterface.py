
import urllib, types, string

def urlencode_data(Dict):
    pairs = []
    for (name, values) in Dict.items():
        ename = urllib.quote(str(name))
        if type(values) != types.ListType:
            values = [values]
        for value in values:
            evalue = urllib.quote(str(value))
            pairs.append( "%s=%s" % (ename, evalue) )
    return string.joinfields(pairs, "&")

def urlpost(url, postdata={}):
    uf = urllib.urlopen(url, urlencode_data(postdata))
    results = uf.read()
    uf.close()
    return(results)

def BugzillaLogin():
    url = "http://abeni.kicks-ass.net/bugzilla/query.cgi?GoAheadAndLogin=1"
    data ={
        "Bugzilla_login":"rob@127.0.0.1",
        "Bugzilla_password":"cakebread",
    }
    res = urlpost(url, data)
    print res

def EnterNewBug():
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
        "assigned_to":"",
        "cc":"",
        "bug_file_loc":"http://",
        "short_desc":"pack-0.2.ebuild (New version)",
        "comment":"This package is a package.",
        "keywords":"",
        "form_name":"enter_bug",
    }
    res = urlpost(url, data)
    print res

if __name__=="__main__":
    import pdb
    #BugzillaLogin()
    EnterNewBug()

