import portage, string, re

settings = portage.config().environ()

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

class ebuild:
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
		
	def __init__(self, filename):
		self.__localinit__()
		
		# check the location
		portdir = settings['PORTDIR']
		overlays = settings['PORTDIR_OVERLAY'].split(" ")
		for d in overlays:
			if filename[:len(d)] == d:
				self.location = d
		if len(self.location) <= 1 and filename[:len(portdir)] == portdir:
			self.location = portdir
		elif len(self.location) <= 1:
			raise Exception("invalid ebuild directory")
			
		s = string.split(filename, "/")
		self.filename = s[len(s)-1]
		self.package = s[len(s)-2]
		self.category = s[len(s)-3]


# test code
sc = ebuild("/usr/portage/local/net-mail/sylpheed-claws-cvs/sylpheed-claws-cvs-0.9.4.ebuild")
print sc.location
print sc.filename
print sc.package
print sc.category
