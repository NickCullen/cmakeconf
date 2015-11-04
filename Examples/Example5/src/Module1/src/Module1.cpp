#include "Module1.h"
#include <stdio.h>

void Module1SayHello()
{
	printf("Hello from Module1\n");
}

void CalledFromModule2()
{
	printf("This is Module1 being called from Module2\nI was included using LinkLibs in Modul2 build.cm file\n");
}