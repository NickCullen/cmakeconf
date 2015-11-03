#include "MyApplication.h"
#include "Module1.h"
#include "Module2.h"

int main(int argc, char** argv)
{
	MyAppSayHello();
	Module1SayHello();
	Module2SayHello();
	
	return 0;
}