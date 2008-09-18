/* _x11_idle: Provide the sleep_until_idle() function on platforms supporting
 * X11's X Screen Saver Extension.
 *
 * Author: Alexandre Vassalotti <alexandre@peadrop.com>
 */  

#include <Python.h>
#include <stdlib.h>             /* for getenv() */
#include <unistd.h>             /* for sleep() */
#include <X11/Xlib.h>
#include <X11/extensions/scrnsaver.h>

static PyObject *
sleep_until_idle(PyObject *self, PyObject *args)
{
    long seconds_before_idle;
    Display *dpy;
    int event_basep, error_basep;
    XScreenSaverInfo saver_info;
    char *display_name = getenv("DISPLAY");

    if (!PyArg_ParseTuple(args, "l", &seconds_before_idle))
        return NULL;

    if (display_name == NULL)
        display_name = ":0.0";
    dpy = XOpenDisplay(display_name);
    if (dpy == NULL) {
        PyErr_SetString(PyExc_OSError, "cannot open X display");
        return NULL;
    }

    if (!XScreenSaverQueryExtension(dpy, &event_basep, &error_basep)) {
        PyErr_SetString(PyExc_OSError,
                        "XScreenSaver extension is not available");
        XCloseDisplay(dpy);
        return NULL;
    }

    for (;;) {
        long time_to_sleep;

        if (!XScreenSaverQueryInfo(dpy, DefaultRootWindow(dpy), &saver_info)) {
            PyErr_SetString(PyExc_OSError,
                            "unable to query XScreenSaver info");
            XCloseDisplay(dpy);
            return NULL;
        }

        /* Workaround for the bug in the DPMS extension which resets the idle
         * time when the display is turned off.
         *
         * If the saversaver is on, there is a chance DPMS is currently
         * enabled. So, we check the current idle time makes sense by
         * comparing it to the time since the saversaver was enabled. If the
         * idle time doesn't make sense, we ignore its value in favour of the
         * saversaver enabled time.
         *
         * We could also query DPMS extension directly, but that would require
         * adding a whole bunch of other setup code and linking against Xext.
         * So to keep things simple, we don't do any of that.
         */
        if (saver_info.state == ScreenSaverOn &&
            saver_info.idle < saver_info.til_or_since &&
            saver_info.til_or_since / 1000 >= seconds_before_idle)
            break;

        /* Get the time, in milliseconds, since the last X event. */
        if (saver_info.idle / 1000 >= seconds_before_idle)
            break;

        time_to_sleep = seconds_before_idle - saver_info.idle / 1000 + 1;
        sleep(time_to_sleep);
    }

    XCloseDisplay(dpy);
    Py_RETURN_NONE;
}

PyMethodDef x11_idle_methods[] = {
    {"_sleep_until_idle", sleep_until_idle, METH_VARARGS, NULL},
};

PyMODINIT_FUNC
init_x11_idle(void)
{
    PyObject *module;

    module = Py_InitModule("_x11_idle", x11_idle_methods);
    if (module == NULL)
        return;
    
    return;
}
