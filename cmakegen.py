from string import Template
from cmake_templates import *

#class which wraps up section data from the .cm file
class Section:
	def __init__(self,sectionID):
		self.name = sectionID
		self.data = dict()
		
	def __str__(self):
		return "{0} = {1}".format(self.name, self.data)
		
	#data is a 2 item tuple containing (key, value)
	def AddData(self, data):
		self.data[data[0]] = data[1]
		
	#data for specific platform
	def AddTargetedData(self, data):
		k = data[0]
		v = data[1]
		if k in self.data:
			self.data[k].append(v)
		else:
			self.data[k] = [v]
		
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
	
#parses key and value readline
def ParseKeyValue(line, seperator='='):
	k = Trim(line.split(seperator)[0])
	v = Trim(line.split(seperator)[1])
	
	if v.startswith('"') and v.endswith('"'): #string (trim off " marks)
		v = v[1:-1]
	elif v.lower() == "true" or v.lower() == "false":
		if v.lower() == "true":
			v = True
		else:
			v = False
	else:
		try:
			v = ParseFloatOrInt(v)
		except ValueError: #silently pass this error - v will be set to the value
			pass
		
	return(k,v)
	
#returns the data part of the required section from the list of sections
def GetSection(name, sections):
	for s in sections:
		if s.name == name:
			return s.data
	return None
	
#function that constructs the Cmake files.
#rootDir is a string for the root directory
#f is the CMakeLists.txt file
#sections is all the sections and their key&value data pairs from build.cm
def CreateCmakeFile(rootDir, f, sections):
	definitions = GetSection("ProjectDefinitions", sections)
	if definitions:
		WriteDefinitions(f,definitions)

	
#parses the .cm file
#rootDir is a string for the root directory
#f is the python loaded build.cm file
def ParseSections(rootDir, f):
	sections = []
	currentSection = None
	for l in f:
		if l.startswith(';'): #comment line
			continue
			
		if l.startswith('['): #beginning of new section
			currentSection = Section(ParseSection(l))
			sections.append(currentSection)
		elif ":" in l: #value whos key is not unique (stored in list)
			data = ParseKeyValue(l,':')
			currentSection.AddTargetedData(data)
		elif "=" in l: #value whos key is unique
			data = ParseKeyValue(l)
			currentSection.AddData(data)
	
	return sections
	
#Runs the process of generating cmake files
#rootDir is a string for the root directory
#f is the python loaded build.cm file
def Generate(rootDir, f):
	sections = ParseSections(rootDir, f)

	#create cmake lists file
	cmakeFile = open(rootDir + "/CmakeLists.txt", "w")
	if cmakeFile:
		#Write project heading
		ps = GetSection("ProjectSettings", sections)
		WriteProjectSettings(cmakeFile, ps)
		
		#construct rest of CmakeFile
		CreateCmakeFile(rootDir, cmakeFile, sections)
	else:
		print("Failed to create cmakeFile at " + rootDir + "/CmakeLists.txt")