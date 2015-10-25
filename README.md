# cmakeconf
A python library which will take a .cm file and generate a CmakeLists.txt file for specified modules.
This is adding another abstracted layer on top of cmake to simplfy projects as well as not needing to learn the cmake syntax.

# Example of a simple project
[ProjectSettings]
MinCmakeVer=2.6				
Name="Example1" 		

[ProjectIncludeDirectories]
/include

[ProjectSourceDirectories]
/src

[Module]
Output=executable