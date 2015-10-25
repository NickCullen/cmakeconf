from string import Template

#-----template objects-----

#for putting a template inside an ifdef guard
TIfGuard = Template("""if(${condition})
${innerbody}
endif()\n""")

#For minimum cmake version and project name
TProjectSettings = Template("""cmake_minimum_required (VERSION ${MinCmakeVer})
project(${Name})
set_property(GLOBAL PROPERTY USE_FOLDERS ${UseFolders})\n""")

#for including a definition
TDefinition = Template("add_definitions(-D${definition})")

#include directories
TIncludeDirectory = Template('include_directories("${dir}")')

#for globbing source files in a dir
TSourceGlob = Template('FILE(GLOB ${source_id} "${dir}/*.cpp")')

#for outputting an executable
TExecutable = Template("add_executable(${project} $${SOURCES})\n")

#template for appending to a cmake variable
TAppendVariable = Template("set( ${var} $${${var}} $${${appendedval}})\n")

#template for setting cmake variable
TMakeVariable = Template('set (${var} ${value})\n')

#-----Write Functions-----
#Puts innerbody into TIfGuard template with the given condition
#then returns the string
def WrapInGuard(condition, innerbody):
	return TIfGuard.substitute(dict(condition=condition, innerbody=innerbody))
	
def WriteProjectSettings(f, section):
	#defaults
	if "UseFolders" not in section.data: section.data["UseFolders"] = "OFF"
	output = TProjectSettings.substitute(section.data)
	f.write(output)
	
def WriteRequiredVariables(f):
	variables = [dict(var="INCLUDES", value='""'), dict(var="SOURCES", value='""'), dict(var="LIBS", value='""') ]
	for v in variables:
		f.write(TMakeVariable.substitute(v))
	
	
def WriteDefinitions(f, sections):
	#first write the one which is not platform specific
	for s in sections:
		defs = s.data[":"]
		
		#gather definitions to be output
		output = ""
		for d in defs:
			output += TDefinition.substitute(dict(definition=d)) + "\n"
			
		#This line look pretty complicated but all it really is doing is writing output
		#to the file if there is no condition. Else it writes the output wrapped in an ifguard to file
		f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))

def WriteIncludeDirectories(f, rootDir, sections):
	#first write the one which is not platform specific
	for s in sections:
		dirs = s.data[":"]
		
		#gather definitions to be output
		output = ""
		for d in dirs:
			d = d if d.startswith('/') else "/"+d
			output += TIncludeDirectory.substitute(dict(dir=rootDir+d)) + "\n"
			
		#This line look pretty complicated but all it really is doing is writing output
		#to the file if there is no condition. Else it writes the output wrapped in an ifguard to file
		f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))
		
def WriteSourceDirectories(f, rootDir, sections):
	#first write the one which is not platform specific
	for s in sections:
		dirs = s.data[":"]

		#gather definitions to be output
		output = ""
		for d in dirs:
			sourceID = d.replace('/','_')
			
			d = d if d.startswith('/') else "/"+d
			output = TSourceGlob.substitute(dict(dir=rootDir+d, source_id=sourceID)) + "\n"
			
			#This line look pretty complicated but all it really is doing is writing output
			#to the file if there is no condition. Else it writes the output wrapped in an ifguard to file
			f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))
			
			#append to SOURCES cmake variable
			f.write(TAppendVariable.substitute(dict(var="SOURCES", appendedval=sourceID)))
		
#Writes the module output section of the CmakeLists file
def WriteModuleOutput(f, m):
	name = m.settings.data["Name"]	#name of lib/exe
	o = m.settings.data["Output"]				#build type (lib/exe)
	if "exe" in o:
		f.write(TExecutable.substitute(dict(project=name)))
	
	return None