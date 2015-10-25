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
TSourceGlob = Template('FILE(GLOB ${source_id} "${dir}/*.c*")')

#for globbing header files in a dir
THeaderGlob = Template('FILE(GLOB ${header_id} "${dir}/*.h*")')

#template for source group (so they appear in VS filters etc.
TSourceGroup = Template('source_group("${folder}" FILES $${${files}})\n')

#for outputting an executable
TExecutable = Template("add_executable(${project} $${SOURCES} $${HEADERS})\n")

#template for appending a cmake variable to another cmake variable
TAppendVariable = Template("set( ${var} $${${var}} $${${appendedval}})\n")

#template for appending a python variable to a cmake variable
TAppendPythonVariable = Template("set( ${var} $${${var}} ${appendedval})\n")

#template for setting cmake variable
TMakeVariable = Template('set (${var} ${value})\n')

#template for adding a link directory
TLinkDirectory = Template('link_directories("${dir}")')

#template for targeting link libs
TTargetLinkLibs = Template("""if(NOT LIBS STREQUAL "")
target_link_libraries(${name} $${LIBS})
endif()
""")

#template for exectuable output
TExecutableOutput = Template('set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${dir}")\n')

#-----Write Functions-----
#Puts innerbody into TIfGuard template with the given condition
#then returns the string
def WrapInGuard(condition, innerbody):
	return TIfGuard.substitute(dict(condition=condition, innerbody=innerbody))
	
def WriteProjectSettings(f, section):
	#defaults
	if "UseFolders" not in section.data: section.data["UseFolders"] = "OFF"
	
	#output
	output = TProjectSettings.substitute(section.data)
	f.write(output)
	
#writes required CMAKE variables to the file
def WriteRequiredVariables(f):
	#all required variables go here to initialise
	variables = [
		dict(var="INCLUDES", value='""'), 
		dict(var="SOURCES", value='""'), 
		dict(var="LIBS", value='""') 
		]
	
	#write them to file	
	for v in variables:
		f.write(TMakeVariable.substitute(v))
	
#definitions such as #defines 	
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

#project include directories
def WriteIncludeDirectories(f, rootDir, sections):
	#first write the one which is not platform specific
	for s in sections:
		dirs = s.data[":"]
		
		#gather definitions to be output
		output = ""
		for d in dirs:
			d = d if d.startswith('/') else "/"+d
			headerID = d.replace('/','_')
			
			#add include directory
			output = TIncludeDirectory.substitute(dict(dir=rootDir+d)) + "\n"
			f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))
			
			#glob all header files
			output = THeaderGlob.substitute(dict(dir=rootDir+d, header_id=headerID)) + "\n"
			f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))
			
			#append to HEADERS variable
			output = TAppendVariable.substitute(dict(var="HEADERS", appendedval=headerID))
			f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))
			
			#make source group so they appear in filters
			d = d.replace('/','\\\\')
			output = TSourceGroup.substitute(dict(folder="Header Files" + d, files=headerID))
			f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))
		
#project source directories
def WriteSourceDirectories(f, rootDir, sections):
	#first write the one which is not platform specific
	for s in sections:
		dirs = s.data[":"]

		output = ""
		for d in dirs:
			d = d if d.startswith('/') else "/"+d
			sourceID = d.replace('/','_')
			
			#glob all source files
			output = TSourceGlob.substitute(dict(dir=rootDir+d, source_id=sourceID)) + "\n"
			f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))
			
			#append globbed source files to SOURCES cmake variable
			output = TAppendVariable.substitute(dict(var="SOURCES", appendedval=sourceID))
			f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))
			
			#make source group so they appear in filters
			d = d.replace('/','\\\\')
			output = TSourceGroup.substitute(dict(folder="Source Files" + d, files=sourceID))
			f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))

#includes local library directories 
def WriteProjectLibDirectories(f, rootDir, sections):
	#first write the one which is not platform specific
	for s in sections:
		dirs = s.data[":"]

		output = ""
		for d in dirs:
			d = d if d.startswith('/') else "/"+d
			
			#include lib directory
			output = TLinkDirectory.substitute(dict(dir=rootDir+d)) + "\n"
			f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))

#adds all libs to the LIBS cmake var
def WriteLinkLibs(f, rootDir, sections):
	#first write the one which is not platform specific
	for s in sections:
		libs = s.data[":"]

		output = ""
		for l in libs:
			#add to LIBS cmake var
			output = TAppendPythonVariable.substitute(dict(var="LIBS", appendedval=l))
			f.write(output if not s.HasCondition() else WrapInGuard(s.condition, output))
			
#Writes the module output section of the CmakeLists file
def WriteModuleOutput(f, rootDir, m):
	name = m.settings.data["Name"]	#name of lib/exe
	t = m.settings.data["Type"]	#build type (lib/exe)
	if "exe" in t:
		#for setting output dir
		if "Output" in m.settings.data:
			o = m.settings.data["Output"]
			o = o if o.startswith('/') else "/"+o
			o = rootDir + o
			f.write(TExecutableOutput.substitute(dict(dir=o)))
			
		f.write(TExecutable.substitute(dict(project=name)))
		f.write(TTargetLinkLibs.substitute(dict(name=name)))
		
	return None
	
