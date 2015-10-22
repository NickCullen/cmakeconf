import * from cmakegen.py
import os

if __name__ == "__main__":
	
	f = open("build.cm")
	rootDir = os.path.dirname(os.path.realpath(__file__))
	
	print(f)
	print(rootDir)
	print("In main")