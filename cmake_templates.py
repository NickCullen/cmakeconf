from string import Template

#For minimum cmake version and project name
TProjectSettings = Template("""cmake_minimum_required (VERSION ${MinCmakeVer})
project(${Name})
set_property(GLOBAL PROPERTY USE_FOLDERS ${UseFolders})""")
def WriteProjectSettings(f, d):
	s = TProjectSettings.substitute(d)
	f.write(s)