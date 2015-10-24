from string import Template

#-----template objects----

#for putting a template inside an ifdef guard
TIfGuard = Template("""if(${condition})
${innerbody}
endif()""")

#For minimum cmake version and project name
TProjectSettings = Template("""cmake_minimum_required (VERSION ${MinCmakeVer})
project(${Name})
set_property(GLOBAL PROPERTY USE_FOLDERS ${UseFolders})\n""")

#for including a definition
TDefinition = Template("add_definitions(-D${definition})")






#-----Write Functions-----
#Puts innerbody into TIfGuard template with the given condition
#then returns the string
def WrapInGuard(condition, innerbody):
	return TIfGuard.substitute(dict(condition=condition, innerbody=innerbody))
	
def WriteProjectSettings(f, section):
	output = TProjectSettings.substitute(section.data)
	f.write(output)
	
	
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
