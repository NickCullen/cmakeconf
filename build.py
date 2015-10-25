import cmakegen as cmake
import os

if __name__ == "__main__":
	
	f = open("build.cm")
	rootDir = os.path.dirname(os.path.realpath(f.name))

	print("rootDir = " + rootDir)
	if f:
		cmake.Generate(rootDir, f)
	else:
		print("Could not find build.cm")