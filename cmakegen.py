#class which wraps up section data from the .cm file
class Section:
	def __init__(self,sectionID):
		self.id = sectionID
		self.data = dict()
		
	def __str__(self):
		return self.id
		
	#data is a 2 item tuple containing (key, value)
	def AddData(self, data):
		self.data[data[0]] = data[1]
		
#trims spaces at start and end of string
def Trim(s):
	return s.strip()
	
#returns string value of section
def ParseSection(line):
	return Trim(line)[1:-1]

#tries to parse to float or int. Will raise error it it is a string
def ParseFloatOrInt(value):
	return float(value) if '.' in value else int(value)
	
#parses key and value readline
def ParseKeyValue(line):
	k = Trim(line.split('=')[0])
	v = Trim(line.split('=')[1])
	
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
	
#Runs the process of generating cmake files
#rootDir is a string for the root directory
#f is the python loaded files
def Generate(rootDir, f):
	
	sections = []
	currentSection = None
	for l in f:
		if l.startswith('['):
			currentSection = Section(ParseSection(l))
			sections.append(currentSection)
		elif "=" in l:
			data = ParseKeyValue(l)
			currentSection.AddData(data)
	
	for section in sections:
		print("section = " + str(section))
		print(section.data)
	