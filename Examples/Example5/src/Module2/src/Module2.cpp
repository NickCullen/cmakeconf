#include "Module2.h"
#include <stdio.h>
#include "Module1.h"

void Module2SayHello()
{
	printf("Hello from Module 2\n");
	CalledFromModule2();		//function belongs in Module1.h
}