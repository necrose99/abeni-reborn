#!/usr/bin/env python

# Copyright (C) 2004 Eric Olinger, http://evvl.rustedhalo.net
# Distributed under the terms of the GNU General Public License, v2 or later
# Author : Eric Olinger <EvvL AT RustedHalo DOT net>

from xml.sax import saxutils, make_parser
from xml.sax.handler import feature_namespaces


class Metadata_XML(saxutils.DefaultHandler):

    def __init__(self):
        saxutils.DefaultHandler.__init__(self)
        self._inside_herd = "No"
        self._inside_maintainer = "No"
        self._inside_email = "No"
        self._inside_name = "No"

        self._herd = []
        self._maintainers = []
        self._name = []

    def startElement(self, tag, attr):
        if tag == "herd":
            self._inside_herd="Yes"
        if tag == "maintainer":
            self._inside_maintainer="Yes"
        if tag == "email":
            self._inside_email="Yes"
        if tag == "name":
            self._inside_name = "Yes"

    def endElement(self, tag):
        if tag == "herd":
            self._inside_herd="No"
        if tag == "maintainer":
            self._inside_maintainer="No"
        if tag == "email":
            self._inside_email="No"
        if tag == "name":
            self._inside_name="No"

    def characters(self, contents):
        if self._inside_herd == "Yes":
            self._herd.append(contents)
            
        if self._inside_maintainer=="Yes" and self._inside_email=="Yes":
            self._maintainers.append(contents)

        if self._inside_name=="Yes":
            self._name.append(contents)

def get_metadata(ebuild_dir):
    """Get dictionary with metadata.xml info"""
    metadata_file= "%s/metadata.xml" % ebuild_dir
    parser = make_parser()
    handler = Metadata_XML()
    parser.setContentHandler(handler)
    parser.parse(metadata_file)
    md = {}
    if handler._herd:
        md['herds'] = handler._herd

    if handler._maintainers:
        md['maintainers'] = handler._maintainers
    if handler._name:
        md['names'] = handler._name
    return md

if __name__ == "__main__":
    print get_metadata("/usr/portage/app-portage/abeni")
