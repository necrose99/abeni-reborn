#!/usr/bin/python

"""
functions for extracting useful info from a pkg URI
such as PN, PV, MY_P, SRC_URI

EXAMPLES:

    http://www.foo.com/pkgfoo-1.0.tbz2
    PN="pkgfoo"
    PV="1.0"
    Ebuild name: pkgfoo-1.0.ebuild
    SRC_URI="http://www.foo.com/${P}.tbz2"

    http://www.foo.com/PkgFoo-1.0.tbz2
    PN="pkgfoo"
    PV="1.0"
    Ebuild name: pkgfoo-1.0.ebuild
    MY_P="PkgFoo-${PV}"
    SRC_URI="http://www.foo.com/${MY_P}.tbz2"

    http://www.foo.com/pkgfoo_1.0.tbz2
    PN="pkgfoo"
    PV="1.0"
    Ebuild name: pkgfoo-1.0.ebuild
    MY_P="${PN}_${PV}"
    SRC_URI="http://www.foo.com/${MY_P}.tbz2"

    http://www.foo.com/PKGFOO_1.0.tbz2
    PN="pkgfoo"
    PV="1.0"
    Ebuild name: pkgfoo-1.0.ebuild
    MY_P="PKGFOO_${PV}"
    SRC_URI="http://www.foo.com/${MY_P}.tbz2"

    http://www.foo.com/pkg-foo-1.0_beta1.tbz2
    PN="pkg-foo"
    PV="1.0_beta1"
    Ebuild name: pkg-foo-1.0_beta1.ebuild
    SRC_URI="http://www.foo.com/${P}.tbz2"

"""


import sys
import urlparse

from portage import pkgsplit

def get_raw_p(uri):
    """return file name minus extension from src_uri"""
    path = urlparse.urlparse(uri)[2]
    path = path.split('/')
    fname = strip_ext(path[len(path)-1])
    return fname

def strip_ext(fname):
    """Strip possible extensions from filename."""
    fname = fname.replace(".zip", "")
    fname = fname.replace(".tgz", "")
    fname = fname.replace(".tar.gz", "")
    fname = fname.replace(".tar.bz2", "")
    fname = fname.replace(".tbz2", "")
    return fname

def validate_uri_scheme(uri):
    """If uri's addressing scheme is valid return 1"""
    if uri[0:5] == "http:":
        return 1
    if uri[0:4] == "ftp:":
        return 1
    if uri[0:7] == "mirror:":
        return 1

def parse_sourceforge_uri(uri):
    """Change uri to mirror://sourceforge format"""
    uri_out, homepage = "", ""
    if uri.find('sourceforge') != -1:
        tst_uri = urlparse.urlparse(uri)
        if tst_uri[2].find('sourceforge') != -1:
            uri_out = 'mirror:/%s' % tst_uri[2]
            homepage = "http://sourceforge.net/projects/%s/" % \
                       tst_uri[2].split("/")[2]
    return uri_out, homepage

def is_good_filename(uri):
    """If filename is sane enough to deduce PN & PV, return pkgsplit results"""
    if validate_uri_scheme(uri):
        psplit = split_p(uri)
        if not psplit:
            return
        if psplit[0].islower():
            return psplit

def split_p(uri):
    p = get_raw_p(uri)
    psplit = pkgsplit(p)
    return psplit

def get_components(uri):
    """Split uri into pn and pv and new uri"""
    p = get_raw_p(uri)
    psplit = split_p(uri)
    uri_out = uri.replace(p, "${P}") 
    pn = psplit[0].lower()
    pv = psplit[1]
    return uri_out, pn, pv

def get_myp(uri):
    """Return MY_P and new uri with MY_P in it"""
    my_p = get_raw_p(uri)
    uri_out = uri.replace(my_p, "${MY_P}") 
    return uri_out, my_p

def guess_components(my_p):
    """Try to break up raw MY_P into PN and PV"""
    pn, pv = "", ""

    # Ok, we just have one automagical test here.
    # We should look at versionator.eclass for inspiration
    # and then come up with several functions.
    uscores = my_p.find("_")
    if uscores != -1:
        my_p = my_p.replace("_", "-")

    psplit = pkgsplit(my_p)
    if psplit:
        pn = psplit[0].lower()
        pv = psplit[1]
    return pn, pv

def test_uri(uri):
    """Given uri, try to determing SRC_URI, ebuild name, MY_P etc"""
    print uri
    if uri.find('sourceforge') != -1:
        new_uri, homepage = parse_sourceforge_uri(uri)
        if new_uri:
            uri = new_uri
            print 'HOMEPAGE="%s"' % homepage
    if is_good_filename(uri):
        uri_out, pn, pv = get_components(uri)
        print 'PN="%s"' % pn
        print 'PV="%s"' % pv
        print "Ebuild name: %s-%s.ebuild" % (pn, pv)
        print 'SRC_URI="%s"' % uri_out
    else:
        uri_out, my_p = get_myp(uri)
        pn, pv = guess_components(my_p)
        if pn and pv:
            print 'PN="%s"' % pn
            print 'PV="%s"' % pv
            my_p = my_p.replace(pn, "${PN}")
            my_p = my_p.replace(pv, "${PV}")
            print "Ebuild name: %s-%s.ebuild" % (pn, pv)
        print 'MY_P="%s"' % my_p
        print 'SRC_URI="%s"' % uri_out
    print
 
if __name__ == "__main__":
    test_uri("http://www.foo.com/pkgfoo-1.0.tbz2")
    test_uri("http://www.foo.com/PKGFOO-1.0.tbz2")
    test_uri("http://www.foo.com/pkgfoo_1.0.tbz2")
    test_uri("http://www.foo.com/PKGFOO_1.0.tbz2")
    test_uri("http://www.foo.com/pkg-foo-1.0_beta1.tbz2")
    test_uri("http://www.foo.com/pkg_foo-1.0lawdy.tbz2")
    test_uri("http://internap.dl.sourceforge.net/sourceforge/abeni/abeni-0.0.22.tar.gz")
    test_uri("http://internap.dl.sourceforge.net/sourceforge/dummy/StupidName_0.2.tar.gz")

