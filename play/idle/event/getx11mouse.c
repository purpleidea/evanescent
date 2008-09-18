#include <stdlib.h>
#include <stdio.h>
#include <X11/Xlib.h>

/**
 * Get the current position of the mouse
 * Compiles on Linux and Solaris with :
 *   gcc -L/usr/X11R6/lib -lX11 getX11Mouse.c -o getX11Mouse
 *
 *   on ubuntu:
 *   apt-get install libx11-dev
 *   gcc -L/usr/X11R6/ -lX11 getx11mouse.c -o getX11Mouse
 *
 * @author Olivier Chafik
 */

int main( int argc, char *argv[] ) {
	Window w, rootWin, win; 
	int x, y, winX, winY; 
	unsigned int stateMask = 0; 

	Display* display = XOpenDisplay(NULL);
	if (!display) exit(1);

	w = XCreateWindow(display, DefaultRootWindow(display), 1, 1, 1, 1, 0, CopyFromParent, InputOnly, CopyFromParent, 0, NULL); 

	if (XQueryPointer( display, w, &rootWin, &win, &x, &y, &winX, &winY, &stateMask)) {
		printf( "@%d,%d\n", x, y ); 
	}

	XCloseDisplay(display);
	return 0; 
}
