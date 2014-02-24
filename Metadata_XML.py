# Copyright (C) 2004 Eric Olinger, http://evvl.rustedhalo.net
# Distributed under the terms of the GNU General Public License, v2 or later
# Author : Eric Olinger <EvvL AT RustedHalo DOT net>
# Contributor(s): David Stanek

from xml.sax import saxutils, make_parser
from xml.sax.handler import feature_namespaces


__version_ = "0.2"


class Metadata_XML_person:
	name = ""
	email = ""
	description = {}


class Metadata_XML_changelog:
	date = ""
	developer = Metadata_XML_person()
	contributor = Metadata_XML_person()
	version = ""
	description = {}
	files = []
	bugid = ""


class Metadata_XML(saxutils.DefaultHandler):
	# Private variable only for parsing
	__tag_ = {}
	__lang_ = "en"

	# User data
	herd = ""
	maintainers = []
	maintainers.append( Metadata_XML_person() )
	longdescription = {}
	changelog = []
	changelog.append( Metadata_XML_changelog() )

	def startElement(self, tag, attr):
		self.__tag_[ tag ] = "Yes"

		if attr.has_key('lang'):
			self.__lang_ = attr.get("lang")
		else:
			self.__lang_ = "en"

	def endElement(self, tag):
		self.__tag_[ tag ] = "No"
	
		if tag == "maintainer":
			self.maintainers.append( Metadata_XML_person() )

		if tag == "change":
			self.changelog.append( Metadata_XML_changelog() )

	def characters(self, contents):
		if self.__tag_['pkgmetadata'] == "Yes":
			if self.__tag_.get('herd') == "Yes":
				self.herd = contents

			if self.__tag_.get('maintainer') == "Yes":
				if self.__tag_.get('name') == "Yes":
					self.maintainers[ -1 ].name = contents
				if self.__tag_.get('description') == "Yes":
					if self.maintainers[ -1 ].description.get( self.__lang_ ):
						self.maintainers[ -1 ].description[ self.__lang_ ] += contents
					else:
						self.maintainers[ -1 ].description[ self.__lang_ ] = contents
				if self.__tag_.get('email') == "Yes":
					self.maintainers[ -1 ].email = contents

			if self.__tag_.get('longdescription') == "Yes":
				if self.longdescription.get( self.__lang_ ):
					self.longdescription[ self.__lang_ ] += contents
				else:
					self.longdescription[ self.__lang_ ] = contents

			if self.__tag_.get('changelog') == "Yes":
				if self.__tag_.get('change') == "Yes":
					if self.__tag_.get('date') == "Yes":
						self.changelog[ -1 ].date = contents
					if self.__tag_.get('developer') == "Yes":
						if self.__tag_.get('email') == "Yes":
							self.changelog[ -1 ].developer.email = contents
						if self.__tag_.get('name') == "Yes":
							self.changelog[ -1 ].developer.name = contents
					if self.__tag_.get('contributor') == "Yes":
						if self.__tag_.get('email') == "Yes":
							self.changelog[ -1 ].contributor.email = contents
						if self.__tag_.get('name') == "Yes":
							self.changelog[ -1 ].contributor.name = contents
					if self.__tag_.get('version') == "Yes":
						self.changelog[ -1 ].version = contents
					if self.__tag_.get('description') == "Yes":
						if self.changelog[ -1 ].description.get( self.__lang_ ):
							self.changelog[ -1 ].description[ self.__lang_ ] += contents
						else:
							self.changelog[ -1 ].description[ self.__lang_ ] = contents
					if self.__tag_.get('file') == "Yes":
						self.changelog[ -1 ].files.append( contents )
					if self.__tag_.get('bug') == "Yes":
						self.changelog[ -1 ].bugid = contents


def parse_metadata_xml( file ):
	parser = make_parser()
	handler = Metadata_XML()
	parser.setContentHandler(handler)
	parser.parse( file )
	handler.changelog.pop()
	handler.maintainers.pop()
	return handler

