import portage, string, re

settings = portage.config().environ()
portdir = settings['PORTDIR']
overlays = settings['PORTDIR_OVERLAY'].split(" ")

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

# test code
sc = ebuild("net-mail", "sylpheed-claws", "0.9.4")
print sc.location
print sc.filename
print sc.category
print sc.package
print sc.version
