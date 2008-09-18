#include <Python.h>
#include <stdlib.h>	/* for getenv() */
#include <X11/Xlib.h>
#include <X11/extensions/dpms.h>
#include <X11/extensions/scrnsaver.h>
#include <X11/Xlib.h>

// Based on code in xprintidle.c for the xprintidle command on linux
// and python help from Alexandre Vassalotti <alexandre@peadrop.com>

/*!
 * This function works around an XServer idleTime bug in the
 * XScreenSaverExtension if dpms is running. In this case the current
 * dpms-state time is always subtracted from the current idletime.
 * This means: XScreenSaverInfo->idle is not the time since the last
 * user activity, as descriped in the header file of the extension.
 * This result in SUSE bug # and sf.net bug #. The bug in the XServer itself
 * is reported at https://bugs.freedesktop.org/buglist.cgi?quicksearch=6439.
 *
 * Workaround: Check if if XServer is in a dpms state, check the current
 * timeout for this state and add this value to the current idle time and
 * return.
 *
 * \param _idleTime an unsigned long value with the current idletime from
 * XScreenSaverInfo->idle
 * \return an unsigned long with the corrected idletime
 */

unsigned long workaroundCreepyXServer(Display *dpy, unsigned long _idleTime) {
	int dummy;
	CARD16 standby, suspend, off;
	CARD16 state;
	BOOL onoff;

	if (DPMSQueryExtension(dpy, &dummy, &dummy)) {
		if (DPMSCapable(dpy)) {
			DPMSGetTimeouts(dpy, &standby, &suspend, &off);
			DPMSInfo(dpy, &state, &onoff);

			if (onoff) {
				switch (state) {
					case DPMSModeStandby:
						/* this check is a littlebit paranoid, but be sure */
						if (_idleTime < (unsigned) (standby * 1000))
							_idleTime += (standby * 1000);
						break;
					case DPMSModeSuspend:
						if (_idleTime < (unsigned) ((suspend + standby) * 1000))
							_idleTime += ((suspend + standby) * 1000);
						break;
					case DPMSModeOff:
						if (_idleTime < (unsigned) ((off + suspend + standby) * 1000))
							_idleTime += ((off + suspend + standby) * 1000);
						break;
					case DPMSModeOn:
					default:
						break;
				}
			}
		} 
	}

	return _idleTime;
}


static PyObject *mouseidle(PyObject *self, PyObject *args) {

	XScreenSaverInfo ssi;
	Display *dpy;
	int event_basep, error_basep;
	char *display_name = getenv("DISPLAY");
	unsigned long result;

	if (display_name == NULL) display_name = ":0.0";
	dpy = XOpenDisplay(display_name);

	if (dpy == NULL) {
		PyErr_SetString(PyExc_OSError, "couldn't open display");
		return NULL;
	}

	if (!XScreenSaverQueryExtension(dpy, &event_basep, &error_basep)) {
		PyErr_SetString(PyExc_OSError, "screen saver extension not supported");
		XCloseDisplay(dpy);
		return NULL;
	}

	if (!XScreenSaverQueryInfo(dpy, DefaultRootWindow(dpy), &ssi)) {
		PyErr_SetString(PyExc_OSError, "couldn't query screen saver info");
		XCloseDisplay(dpy);
		return NULL;
	}

	result = workaroundCreepyXServer(dpy, ssi.idle);
	XCloseDisplay(dpy);
	return Py_BuildValue("i", result);

}


PyMethodDef x11_idle_methods[] = {
	{"_mouseidle", mouseidle, METH_VARARGS, NULL},
};

PyMODINIT_FUNC init_x11_idle(void) {
	PyObject *module;

	module = Py_InitModule("_x11_idle", x11_idle_methods);
	if (module == NULL) return;

	return;
}

