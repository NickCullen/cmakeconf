cmake_minimum_required (VERSION 2.6)
project(Vici)

# Turn on the ability to create folders to organize projects (.vcproj)
# It creates "CMakePredefinedTargets" folder by default and adds CMake
# defined projects like INSTALL.vcproj and ZERO_CHECK.vcproj
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

#add preprocessor definitions
if(VICI_WINDOWS)
 	add_definitions(-DVICI_WINDOWS -DVICI_DESKTOP -DVICI_OPENGL -D_CRT_SECURE_NO_WARNINGS)
elseif(VICI_MAC)
	add_definitions(-DVICI_MAC -DVICI_DESKTOP -DVICI_OPENGL)
endif()

#set ThirdParty include path
set(THIRD_PARTY "${PROJECT_SOURCE_DIR}/ThirdParty")

##glob all common third party headers and sources
FILE(GLOB squirrel_source "ThirdParty/squirrel/src/*.c*")
FILE(GLOB squirrel_h "ThirdParty/squirrel/*.h*")

#add third party includes
include_directories("${THIRD_PARTY}")
include_directories("${THIRD_PARTY}/squirrel")

#engine includes
set(VICI_INCLUDES "${PROJECT_SOURCE_DIR}/include")
include_directories("${VICI_INCLUDES}")
include_directories("${VICI_INCLUDES}/core")
include_directories("${VICI_INCLUDES}/rendering")
include_directories("${VICI_INCLUDES}/util")
include_directories("${VICI_INCLUDES}/datastructures")
include_directories("${VICI_INCLUDES}/assets")
include_directories("${VICI_INCLUDES}/debugging")

#group them
source_group("Header\\Squirrel" FILES ${squirrel_h})
source_group("Source\\Squirrel" FILES ${squirrel_source})

#get module sources
FILE(GLOB core "src/core/*.cpp")
FILE(GLOB rendering "src/rendering/*.cpp")
FILE(GLOB util "src/util/*.cpp")
FILE(GLOB datastructures "src/datastructures/*.cpp")
FILE(GLOB assets "src/assets/*.cpp")
FILE(GLOB debugging "src/debugging/*.cpp")

#get module headers
FILE(GLOB core_h "${VICI_INCLUDES}/core/*.h*")
FILE(GLOB rendering_h "${VICI_INCLUDES}/rendering/*.h*")
FILE(GLOB util_h "${VICI_INCLUDES}/util/*.h*")
FILE(GLOB datastructures_h "${VICI_INCLUDES}/datastructures/*.h*")
FILE(GLOB assets_h "${VICI_INCLUDES}/assets/*.h*")
FILE(GLOB debugging_h "{VICI_INCLUDES}/debugging/*.h*")

#group them so visual studio will organise them
source_group("Source\\Core" FILES ${core})
source_group("Header\\Core" FILES ${core_h})
source_group("Source\\Rendering" FILES ${rendering})
source_group("Header\\Rendering" FILES ${rendering_h})
source_group("Source\\Util" FILES ${util})
source_group("Header\\Util" FILES ${util_h})
source_group("Source\\Datastructures" FILES ${datastructures})
source_group("Header\\Datastructures" FILES ${datastructures_h})
source_group("Source\\AssetLoading" FILES ${assets})
source_group("Header\\AssetLoading" FILES ${assets_h})
source_group("Source\\Debugging" FILES ${debugging})
source_group("Header\\Debugging" FILES ${debugging_h})

#do the same with the global engine includes for reference
FILE(GLOB thirdparty_h "${THIRD_PARTY}/*.h*")
source_group("ThirdParty" FILES ${thirdparty_h})

#windows build
if(VICI_WINDOWS)
	message("WINDOWS BUILD")

	#link up win32 lib dir
	if("${CMAKE_SIZEOF_VOID_P}" EQUAL "8")
		message("BUILDING FOR x64")
		link_directories("${THIRD_PARTY}/lib/win64")
	else("${CMAKE_SIZEOF_VOID_P}" EQUAL "8")
		message("BUILDING FOR x86")
		link_directories("${THIRD_PARTY}/lib/win32")
	endif("${CMAKE_SIZEOF_VOID_P}" EQUAL "8")

	#find required libaries
	find_package(OpenGL REQUIRED)

	#include required libraries headers
	include_directories(${OPENGL_INCLUDE_DIRS})

	#get all windows specific source files
	FILE(GLOB platform_sources "src/windows/*.cpp")

	#set the extra libs so that they will be compiled
	set(EXTRA_LIBS glfw3 glew32 pthreadVC2 ${OPENGL_LIBRARIES})

	#set the extra libs so that they will be compiled
	set(EXTRA_LIBS_DEBUG vld)
elseif(VICI_MAC)
	message("MAC BUILD")
	#include the apple frameworks dir
	include_directories("/System/Library/Frameworks")

	#link up mac lib dir
	link_directories("${THIRD_PARTY}/lib/mac")

	#find required libaries
	find_package(OpenGL REQUIRED)
	find_library(COCOA_LIB cocoa)
	find_library(IOKIT_LIB IOKit)
	find_library(COREVIDEO_LIB CoreVideo)

	MARK_AS_ADVANCED (COCOA_LIB
	                 IOKIT_LIB
	                 COREVIDEO_LIB)

	#include required libraries headers
	include_directories(${OPENGL_INCLUDE_DIRS})

	#get all mac specific source files
	FILE(GLOB platform_sources "src/mac/*.cpp")

	#set the extra libs so that they will be compiled
	set(EXTRA_LIBS ${COCOA_LIB} ${IOKIT_LIB} ${COREVIDEO_LIB} ${OPENGL_LIBRARIES} glfw3 pthread)
endif()

#compile engine sources into vici library
add_library(vici STATIC ${core} ${rendering} ${util} ${datastructures} ${assets} ${debugging} ${platform_sources} ${squirrel_source}
							${core_h} ${rendering_h} ${util_h} ${datastructures_h} ${assets_h} ${debugging_h} ${thirdparty_h} ${squirrel_h})	#header files need to be included so they get added to the vs filters


