
all:
	gcc -shared -fPIC -I /usr/include/python2.6/ -I /usr/include/GL/ SYNModule/module.c -lpython2.6 -o SYNModule/synmod.so
	cp SYNModule/synmod.so Core


clean:
	rm Core/synmod.so
	rm SYNModule/synmod.so
