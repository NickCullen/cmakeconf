#include "player.h"
#include <stdio.h>

int main(int argc, char** argv)
{
#ifdef SAYGOODBYE
	printf("Goodbye, World!\n");
#else
	printf("Hello, World!\n");
#endif
	
	return 0;
}