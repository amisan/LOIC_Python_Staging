
all:
	gcc -shared -fPIC -I /usr/include/python2.7/  SYNModule/module.c -o Core/synmod.so


clean:
	rm Core/synmod.so
