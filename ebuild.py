import portage, string, re, os

settings = portage.config().environ()
portdir = settings['PORTDIR']
overlays = settings['PORTDIR_OVERLAY'].split(" ")

# error codes
ERR_FILE_NOT_FOUND  = 1
ERR_SYNTAX 			= 2

class element:
	def __init__(self, pos, etype = "unknown", content = ""):
		self.pos = pos
		self.content = content
		self.type = etype
		
	def getPos(self):
		return self.pos
		
	def getContent(self):
		return self.content
		
	def addContent(self, newcontent):
		self.content += newcontent
		
	def getType(self):
		return self.type
	
# class that encapsulates all the data from an ebuild
class ebuild:
	# kind of default constructor to set all fields to sane values
	def __localinit__(self):
		self.filename = ""
		self.location = ""
		self.category = ""
		self.package = ""
		self.version = ""
		
		self.elements = { "functions": [], "variables": [], "statements": [] }
		self.header = ""

		self.content = ""
				
	# constructor to get the ebuild by filename
	def __init__(self, filename):
		self.__localinit__()
		
		# check the location
		allportdirs = portdir + overlays
		for d in allportdirs:
			if filename[:len(d)] == d:
				self.location = d
		if len(self.location) <= 1:
			raise Exception("invalid ebuild directory")

		if self.location[-1] == "/":
			self.location = self.location[:-1]
			
		s = string.split(filename, "/")
		self.filename = s[len(s)-1]
		self.package = s[len(s)-2]
		self.category = s[len(s)-3]
		
		# use portage to get the version part
		self.version = portage.catpkgsplit(self.category+"/"+self.filename.replace(".ebuild", ""))
		if self.version[3] == "r0":
			self.version = self.version[2]
		else:
			self.version = self.version[2]+"-"+self.version[3]

		self.path = self.location+"/"+self.category+"/"+self.package+"/"+self.filename

	# constructor to get the ebuild by location, category, package and version
	def __init__(self, category, package, version, location=portdir):
		self.__localinit__()

		self.location = location
		if self.location[-1] == "/":
			self.location = self.location[:-1]
		self.category = category
		self.package = package
		self.version = version
		self.filename = package+"-"+version+".ebuild"
		self.path = self.location+"/"+self.category+"/"+self.package+"/"+self.filename
		
	# read and parse the ebuild
	def readEbuild(self):
		if not os.path.exists(self.path):
			return ERR_FILE_NOT_FOUND
		
		# check for bash syntax errors
		if os.system("/bin/bash -n " + self.path) != 0:
			return ERR_SYNTAX

		# read the complete content
		myfile = open(self.path, "r")
		self.content = myfile.readlines()
		myfile.close()
		
		# now parse the whole thing
		ln = 0	# linenumber
		l = ""	# current line
		pos = 0	# current element position
		header_finished = False
		myelement = None
		tmpcontent = ""
		while ln < len(self.content):
			l = self.content[ln]
			ln += 1
			
			# check for header
			if not header_finished and l[0] == "#":
				self.header += l
				continue
			header_finished = True
			
			# now read the different elements (functions, variables, statements)
			if myelement == None and l[0] == "#":	# no current element and line is a comment
				tmpcontent +=l						# add line to temporary content
				continue
			elif myelement != None and l[0] == "#":	# we have a element and line is a comment
				myelement.addContent(l)				# add line to current element
				continue

			vartest = re.search('^[A-Z]+.*= ?', l)
			functest = re.search('^[a-zA-Z]*[_a-zA-Z0-9]* ?\(\) ?{', l)
			
			if vartest:
				v = l
				#Multi-line variables
				if (l.count('"') - l.count('\\\"')) == 1:
					while (self.content[ln].count('"') - self.content[ln].count('\\\"')) != 1:
						l = self.content[ln]
						ln += 1
						v += l
					l = self.content[ln]
					ln += 1
					v += l
				myelement = element(pos, "variable", string.strip(tmpcontent+"\n"+v+"\n"))
				pos += 1
				self.elements['variables'].append(myelement)
				myelement = None
				tmpcontent = ""
				continue
			if functest:
				myelement = element(pos, "variable", tmpcontent+"\n")
				pos += 1
				while l.strip() != "}":
					myelement.addContent(l)
					l = self.content[ln]
					ln += 1
				myelement.addContent(l)
				self.elements['functions'].append(myelement)
				myelement = None
				tmpcontent = ""
				continue
			if l.strip() == "":
				continue
			if myelement == None:
				myelement = element(pos, "statement", tmpcontent+"\n"+l)
				pos += 1
			else:
				myelement.addcontent(l)
			self.elements['statements'].append(myelement)
			myelement = None
			
# test code
sc = ebuild("dev-php", "mod_php", "4.3.2")
sc.readEbuild()
print sc.header
for v in sc.elements['variables']:
	print v.getPos(), v.getContent()
for f in sc.elements['functions']:
	print f.getPos(), f.getContent()
for s in sc.elements['statements']:
	print s.getPos(), s.getContent()
