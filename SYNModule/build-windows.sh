#This requires cygwin.
gcc -shared -I /usr/include/Python2.6 -L /usr/lib/Python2.6 windows-module.c -lpython26 -lws2_32 -export-all-symbols -o synmod.pyd
