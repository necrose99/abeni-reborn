import portage, string, re, os

settings = portage.config().environ()
portdir = settings['PORTDIR']
overlays = settings['PORTDIR_OVERLAY'].split(" ")

# error codes
ERR_FILE_NOT_FOUND  = 1
ERR_SYNTAX 			= 2

class eclass:
	def __init__(self, name):
		self.name = name

class function:
	def __init__(self, name):
		self.name = name
		
class variable:
	def __init__(self, name, value):
		self.name = name
		self.value = value

class statement:
	def __init__(self, cmdline):
		self.command = cmdline

# class that encapsulates all the data from an ebuild
class ebuild:
	# kind of default constructor to set all fields to sane values
	def __localinit__(self):
		self.filename = ""
		self.location = ""
		self.category = ""
		self.package = ""
		self.version = ""
		
		self.eclass = []
		self.functions = []
		self.variables = []
		self.header = ""
		self.statements = []

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
		pos = 1	# current element position
		header_finished = False
		for l in self.content:
			ln += 1
			if not header_finished and l[0] == "#":
				self.header += l
				continue
			header_finished = True
			
				
# test code
sc = ebuild("net-mail", "sylpheed-claws", "0.9.4", "/usr/portage/local")
sc.readEbuild()
print sc.header
