from string import Template

#-----template objects-----

#for putting a template inside an ifdef guard
TIfGuard = Template("""if(${condition})
${innerbody}
endif()\n""")

#For minimum cmake version and project name
TProjectSettings = Template("""cmake_minimum_required (VERSION ${MinCmakeVer})
project(${Name})
set_property(GLOBAL PROPERTY USE_FOLDERS ${UseFolders})
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)\n""")


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

#for outputting a shared library
TSharedLib = Template("add_library(${project} SHARED $${SOURCES} $${HEADERS})\n")

#for outputting a static library
TStaticLib = Template("add_library(${project} STATIC $${SOURCES} $${HEADERS})\n")

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

#for linking a framework on the mac
TLinkFramework = Template("""find_library(${framework}_LIB ${framework})
MARK_AS_ADVANCED(${framework}_LIB)
set(LIBS $${LIBS} $${${framework}_LIB})""")

#template for exectuable output
TExecutableOutput = Template('set(EXECUTABLE_OUTPUT_PATH "${dir}")\n')

#template for exectuable output
TRuntimeOutput = Template('set(RUNTIME_OUTPUT_DIRECTORY "${dir}")\n')

#template for library output
TLibraryoutput = Template('set(LIBRARY_OUTPUT_PATH "${dir}")\n')

#template for including a submodule
TSubmoduleInclude = Template('add_subdirectory(${dir})')

#-----Helper Functions----
def WriteToFile(f, output, condition = False, conditionID = ""):
	f.write(output if not condition else WrapInGuard(conditionID, output))

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
		
		WriteToFile(f,output, s.HasCondition(), s.condition)

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
			WriteToFile(f,output, s.HasCondition(), s.condition)
			
			#glob all header files
			output = THeaderGlob.substitute(dict(dir=rootDir+d, header_id=headerID)) + "\n"
			WriteToFile(f,output, s.HasCondition(), s.condition)
			
			#append to HEADERS variable
			output = TAppendVariable.substitute(dict(var="HEADERS", appendedval=headerID))
			WriteToFile(f,output, s.HasCondition(), s.condition)
			
			#make source group so they appear in filters
			d = d.replace('/','\\\\')
			output = TSourceGroup.substitute(dict(folder="Header Files" + d, files=headerID))
			WriteToFile(f,output, s.HasCondition(), s.condition)
		
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
			WriteToFile(f,output, s.HasCondition(), s.condition)
			
			#append globbed source files to SOURCES cmake variable
			output = TAppendVariable.substitute(dict(var="SOURCES", appendedval=sourceID))
			WriteToFile(f,output, s.HasCondition(), s.condition)
			
			#make source group so they appear in filters
			d = d.replace('/','\\\\')
			output = TSourceGroup.substitute(dict(folder="Source Files" + d, files=sourceID))
			WriteToFile(f,output, s.HasCondition(), s.condition)

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
			WriteToFile(f,output, s.HasCondition(), s.condition)

#adds all libs to the LIBS cmake var
def WriteLinkLibs(f, rootDir, sections):
	#first write the one which is not platform specific
	for s in sections:
		libs = s.data[":"]

		output = ""
		for l in libs:
			if not "-framework" in l:
				#add to LIBS cmake var
				output = TAppendPythonVariable.substitute(dict(var="LIBS", appendedval=l))
				WriteToFile(f,output, s.HasCondition(), s.condition)
			else:
				frameworkName = l.replace("-framework ", "")
				frameworkName = frameworkName.strip()
				
				output = TLinkFramework.substitute(dict(framework=frameworkName))
				WriteToFile(f,output, s.HasCondition(), s.condition)
			
			
#Writes the cmake runtime/lib etc. outputs
def WriteOutputs(f, rootDir, sections):
	for s in sections:
		if "Executable" in s.data:
			runtime = s.data["Executable"]
			runtime = runtime if runtime.startswith('/') else "/"+runtime
			runtime = rootDir + runtime
			output = TRuntimeOutput.substitute(dict(dir=runtime))
			WriteToFile(f,output, s.HasCondition(), s.condition)
			
		if "Runtime" in s.data:
			runtime = s.data["Runtime"]
			runtime = runtime if runtime.startswith('/') else "/"+runtime
			runtime = rootDir + runtime
			output = TExecutableOutput.substitute(dict(dir=runtime))
			WriteToFile(f,output, s.HasCondition(), s.condition)
			
		if "Libs" in s.data:
			print("LIBS OUTPUT BEING SET")
			statics = s.data["Libs"]
			statics = statics if statics.startswith('/') else "/"+statics
			statics = rootDir + statics
			output = TLibraryoutput.substitute(dict(dir=statics))
			WriteToFile(f,output, s.HasCondition(), s.condition)
			
			
#Writes the module output section of the CmakeLists file
def WriteModuleOutput(f, rootDir, m):
	name = m.settings.data["Name"]	#name of lib/exe
	t = m.settings.data["Type"]	#build type (lib/exe)
	if "exe" in t:
		f.write(TExecutable.substitute(dict(project=name)))
		f.write(TTargetLinkLibs.substitute(dict(name=name)))
	elif "shared" in t:
		f.write(TSharedLib.substitute(dict(project=name)))
		f.write(TTargetLinkLibs.substitute(dict(name=name)))
	elif "static" in t:
		f.write(TStaticLib.substitute(dict(project=name)))
		f.write(TTargetLinkLibs.substitute(dict(name=name)))
		
	return None
	

#writes the include for a submodule
def WriteSubmoduleIncludes(f, rootDir, sections):
	for s in sections:
		submods = s.data[":"]
		
		for sm in submods:
			sm = sm if sm.startswith('/') else "/"+sm
			
			output = TSubmoduleInclude.substitute(dict(dir=rootDir+sm)) + "\n"
			WriteToFile(f,output, s.HasCondition(), s.condition)