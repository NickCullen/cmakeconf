# cmakeconf
A python library which will take a .cm file and generate a CmakeLists.txt file for specified modules.
This is adding another abstracted layer on top of cmake to simplfy projects as well as not needing to learn the cmake syntax.

#### Specifiable Options (so far)
###### [ProjectSettings]
Simple settings for the project such as:
- Project Name
- Minimum CMAKE version
- UseFolders ON | OFF (for using visual studio folders in solution file)

###### [ProjectDefinitions]
Any #define for the project

###### [ProjectIncludeDirectories]
Point to any include directories the project may need.

###### [ProjectSourceDirectories]
Point to any source directories the project may need.

###### [Module] 
The output of this module and the name of the output. So far options are:
- Name
- Output = executable | exe

#### Notes
To include a section for a specific build target, you can do so by adding [<target>:<SectionName>]

For example, if you wanted to specify certain include directories on a Win32 build target you can do the following
[Win32:ProjectIncludeDirectories]

#### Examples
###### Example1 
Example 1 consists of a simple project with one include directory and one source directory with no libs.
Output is a single executable file.
