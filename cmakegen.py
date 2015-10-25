from string import Template
from cmake_templates import *

#class which wraps up section data from the .cm file
class Section:
	def __init__(self,sectionID):
		self.name = Trim(sectionID)	#name of section
		self.data = dict()			#its collection of data
		self.data[":"] = []			#anything wth a key of : means we only care about its value
		self.condition=""			#name of platform this section is for
		
		#set if this section is only relevant to a certain condition (i.e. certain platform)
		if ":" in sectionID:
			k,v = sectionID.split(':')
			self.condition = Trim(k)
			self.name = Trim(v)
			
		self.identifier = self.name + self.condition	#identifier is a unique id for each section
		
	def __str__(self):
		if self.HasCondition():
			return "{0}({1}) = {2}".format(self.name, self.condition, self.data)
		else:
			return "{0} = {1}".format(self.name, self.data)
	
	#reutrns true if this sections data belongs to a specific platform/condition
	def HasCondition(self):
		return self.condition != ""
		
	#data is a 2 item tuple containing (key, value)
	def AddData(self, data):
		k = data[0]
		if k != ":":
			self.data[data[0]] = data[1]
		else:
			self.data[":"].append(data[1])
		
class Module:
	settings = None				#settings for this module
	projectSettings = None		#settings for this project
	definitions = None			#definitions for this module
	includes = None				#includes for this module
	sources = None				#list of source sections (note some may be for targeted platforms) for this module
	
	def __init__(self):
		return None
		
	#returns a list containing all the source cmake variables
	def GetSourceList(self):
		for s in self.sources:
			print(s)
			
	#returns true if this module is for a specific platform target
	def HasCondition(self):
		return self.settings.HasCondition()
	
#make sure comment is extracted
def ExtractComment(s):
	try:
		index = s.index(';')
		return s[0:index]
	except:
		return s

#trims spaces at start and end of string
def Trim(s):
	return ExtractComment(s).strip()
	
#returns string value of section
def ParseSection(line):
	return Trim(line)[1:-1]

#tries to parse to float or int. Will raise error it it is a string
def ParseFloatOrInt(value):
	return float(value) if '.' in value else int(value)
	
#takes a single string and returns it in its required variable form
def StringToVar(s):
	if s.startswith('"') and s.endswith('"'): #string (trim off " marks)
		s = s[1:-1]
	elif s.lower() == "true" or s.lower() == "false": #bool
		if s.lower() == "true":
			s = True
		else:
			s = False
	else: #might be number or float - try to parse (if error it is a string without quotations)
		try:
			s = ParseFloatOrInt(s)
		except ValueError: #silently pass this error - s will be set to the value
			pass
	return s
			
#parses key and value and returns a 2 tuple (k,v)
def ParseKeyValue(line, seperator='='):
	k = Trim(line.split(seperator)[0])
	v = Trim(line.split(seperator)[1])
	
	v = StringToVar(v)
		
	return(k,v)
	
#parses a line containing a single value
def ParseValue(line):
	v = Trim(line)
	return StringToVar(v)
	
#returns an array of sections given the input name
def GetSections(name, sections):
	ret = []
	for s in sections:
		if name in s.identifier:
			ret.append(s)
	return ret
	
#returns a section whos identifier matches the given name exactly
def GetSectionByIdentifier(name, sections):
	for s in sections:
		if name == s.identifier:
			return s
	return None

#parses the .cm file
#rootDir is a string for the root directory
#f is the python loaded build.cm file
def ParseSections(rootDir, f):
	sections = []
	currentSection = None
	for line in f:
		
		#must trim so we can handle empty lines more easily
		l = Trim(line)
		
		if l.startswith(';') or l == "": #comment or empty string - get next
			continue
			
		if l.startswith('['): #beginning of new section
			currentSection = Section(ParseSection(l))
			sections.append(currentSection)
		elif "=" in l: #value whos key is unique
			data = ParseKeyValue(l)
			currentSection.AddData(data)
		else: #must asume it is just a single value
			val = ParseValue(l)
			currentSection.AddData((":",val))
			
	
	return sections
	
#function that constructs the Cmake files.
#rootDir is a string for the root directory
#f is the CMakeLists.txt file
#sections is all the sections and their key&value data pairs from build.cm
def CreateCmakeFile(rootDir, f, sections):
	module = Module()
	
	ps = GetSectionByIdentifier("ProjectSettings", sections)
	if ps:
		WriteProjectSettings(f, ps)
		module.projectSettings = ps
			
	#write required variables such as INCLUDES, SOURCES and LIBS
	WriteRequiredVariables(f)
	
	definitions = GetSections("ProjectDefinitions", sections)	#get list of definition sections in file
	if definitions:
		WriteDefinitions(f,definitions)
		module.definitions = definitions
		
	includes = GetSections("ProjectIncludeDirectories", sections)
	if includes:
		WriteIncludeDirectories(f, rootDir, includes)
		module.includes = includes
		
	sources = GetSections("ProjectSourceDirectories", sections)
	if sources:
		WriteSourceDirectories(f, rootDir, sources)
		module.sources = sources
		
	moduleSettings = GetSectionByIdentifier("Module", sections)
	if moduleSettings:
		module.settings = moduleSettings
		WriteModuleOutput(f, module)
		
	return module
		
#Runs the process of generating cmake files
#rootDir is a string for the root directory
#f is the python loaded build.cm file
def Generate(rootDir, f):
	sections = ParseSections(rootDir, f)

	#create cmake lists file
	cmakeFile = open(rootDir + "/CmakeLists.txt", "w")
	if cmakeFile:
		#construct rest of CmakeFile
		CreateCmakeFile(rootDir, cmakeFile, sections)
	else:
		print("Failed to create cmakeFile at " + rootDir + "/CmakeLists.txt")
