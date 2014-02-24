#!/usr/bin/env python

import sys
from Metadata_XML import parse_metadata_xml

handler = parse_metadata_xml( "metadata.xml" )

try:
    lang = handler.maintainers[0].description.keys()[0]
except:
    lang = handler.longdescription.keys()[0]

def GetHerds():
    try:
        return handler.herd
    except:
        print "!!! Error - No herd element."
        sys.exit(1)

def GetMaintainers():
    if len(handler.maintainers):
        return handler.maintainers

def GetLongDesc():
    try:
        desc = handler.longdescription[lang]
    except:
        pass

herds = GetHerds() 
m = GetMaintainers()
if m:
    for maintainer in handler.maintainers:
        print maintainer.name + " <" + maintainer.email + ">"
        print maintainer.description[lang]
