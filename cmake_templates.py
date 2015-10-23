from string import Template

#-----template objects----

#for putting a template inside an ifdef guard
TIfGuard = Template("""if(${condition})
\t${innerbody}
endif()""")

#For minimum cmake version and project name
TProjectSettings = Template("""cmake_minimum_required (VERSION ${MinCmakeVer})
project(${Name})
set_property(GLOBAL PROPERTY USE_FOLDERS ${UseFolders})\n""")

#for including a definition
TDefinition = Template("add_definitions(-D${definition})")






#-----Write Functions-----
def WriteProjectSettings(f, d):
	s = TProjectSettings.substitute(d)
	f.write(s)
	
	
def WriteDefinitions(f, d):
	for k,v in d.iteritems():
		if k.lower() != "shared": #platform specific
			for item in v:
				s = TDefinition.substitute(dict(definition=item))
				f.write(TIfGuard.substitute(dict(condition=k, innerbody=s)))
				f.write("\n")
		else: #shared 
			for item in v: #loop through all the shared definitions and output them to the file
				f.write(TDefinition.substitute(dict(definition=item)))
				f.write("\n")