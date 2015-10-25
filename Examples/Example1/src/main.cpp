#include "player.h"
#include <stdio.h>

int main(int argc, char** argv)
{
#ifdef SAYGOODBYE
	printf("Goodbye, World!");
#else
	printf("Hello, World!");
#endif
	
	return 0;
}