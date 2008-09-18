/* Python extension module for interacting with the Windows Terminal Service API.
 * Currently, this only can listing logged-in users and logging them off forcibly.
 *
 * Author: Alexandre Vassalotti <alexandre@peadrop.com>
 * License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.txt>
 */

#include "Python.h"
#include "structseq.h"

#define WIN32_LEAN_AND_MEAN     /* Include only the essential stuff. */
#include <windows.h>
#include <wtsapi32.h>
#if !(WINVER >= 0x0500)
#error "This modules only works with Windows 2000 and newer."
#endif

PyDoc_STRVAR(wts_doc,
"Simple Python interface to the Windows Terminal Service API.");

static PyStructSequence_Field struct_session_info_fields[] = {
	{"id", NULL},
	{"state", NULL},
	{"username", NULL},
	{0} /* sentinel */
};

static PyStructSequence_Desc struct_session_info_desc = {
	"wts.SessionInfo",
	NULL,
	struct_session_info_fields,
	3,
};

static PyTypeObject StructSessionInfoType;
static int initialized = 0;

static HANDLE
open_wts_server(void)
{
    wchar_t buffer[MAX_COMPUTERNAME_LENGTH + 1];
    DWORD buffer_size = sizeof(buffer);
    HANDLE server = NULL;

    if (!GetComputerNameW(buffer, &buffer_size)) {
        PyErr_Format(PyExc_OSError, 
                     "GetComputerNameW failed (%d)", GetLastError());
        return NULL;
    }
    server = WTSOpenServerW(buffer);
    if (server == NULL) {
        PyErr_Format(PyExc_OSError, 
                     "WTSOpenServerW failed (%d)", GetLastError());
        return NULL;
    }
    return server;
}

static PyObject *
wts_listusers(PyObject *self, PyObject *args)
{
    HANDLE server = NULL;
    DWORD session_count;
    WTS_SESSION_INFOW *session_infos = NULL;
    int i, ok;
    PyObject *users = NULL;

    users = PyList_New(0);
    if (users == NULL)
        return NULL;

    server = open_wts_server();
    if (server == NULL)
        goto error;

    ok = WTSEnumerateSessionsW(server, 0, 1, &session_infos, &session_count);
    if (!ok) {
        PyErr_Format(PyExc_OSError, "WTSEnumerateSessionsW failed (%d)",
                     GetLastError());
        goto error;
    }
    for (i = 0; i != session_count; i++) {
        wchar_t *username_raw;
        DWORD username_size;
        PyObject *username_str;
        PyObject *value;
        PyObject *session_info;

        session_info = PyStructSequence_New(&StructSessionInfoType);
        if (session_info == NULL)
            goto error;

        ok = WTSQuerySessionInformationW(server,
                                         session_infos[i].SessionId,
                                         WTSUserName,
                                         &username_raw,
                                         &username_size);
        if (!ok) {
            PyErr_Format(PyExc_OSError, 
                         "WTSQuerySessionInformationW failed (%d)",
                         GetLastError());
            Py_DECREF(session_info);
            goto error;
        }
        username_str = PyUnicode_FromWideChar(
            username_raw, username_size / sizeof(*username_raw) - 1);

        value = PyInt_FromLong(session_infos[i].SessionId);
        PyStructSequence_SET_ITEM(session_info, 0, value);

        value = PyInt_FromLong(session_infos[i].State);
        PyStructSequence_SET_ITEM(session_info, 1, value);

        PyStructSequence_SET_ITEM(session_info, 2, username_str);

        PyList_Append(users, session_info);
        WTSFreeMemory(username_raw);
    }
    WTSFreeMemory(session_infos);
    WTSCloseServer(server);

    return users;

error:
    Py_XDECREF(users);
    if (session_infos)
        WTSFreeMemory(session_infos);
    if (server)
        WTSCloseServer(server);
    return NULL;
}

static PyObject *
wts_logoff(PyObject *self, PyObject *obj)
{
    HANDLE server;
    long session_id;

    session_id = PyInt_AsLong(obj);
    if (PyErr_Occurred())
        return NULL;
    if (session_id < 0) {
        PyErr_SetString(PyExc_ValueError, 
                        "session ID must be non-negative");
        return NULL;
    }
    server = open_wts_server();
    if (server == NULL)
        return NULL;

    if (!WTSLogoffSession(server, session_id, 1 /* wait */)) {
        PyErr_Format(PyExc_OSError,
                     "WTSLogoffSession failed (%d)", GetLastError());
        WTSCloseServer(server);
        return NULL;
    }

    WTSCloseServer(server);

    Py_RETURN_NONE;
}

static PyObject *
wts_logmeoff(PyObject *self, PyObject *args)
{
    DWORD session_id;

    if (!ProcessIdToSessionId(GetCurrentProcessId(), &session_id)) {
        PyErr_Format(PyExc_OSError,
                     "ProcessIdToSessionId failed (%d)", GetLastError());
        return NULL;
    }
    return wts_logoff(self, PyInt_FromLong(session_id));
}

static PyObject *
wts_shutdown(PyObject *self, PyObject *args)
{
    HANDLE server;

    server = open_wts_server();
    if (server == NULL)
        return NULL;

    if (!WTSShutdownSystem(server, WTS_WSD_POWEROFF)) {
        PyErr_Format(PyExc_OSError,
                     "WTSShutdownSystem failed (%d)", GetLastError());
        return NULL;
    }

    WTSCloseServer(server);

    Py_RETURN_NONE;
}

static PyMethodDef wts_methods[] = {
    {"listusers", wts_listusers, METH_NOARGS, NULL},
    {"logoff", wts_logoff, METH_O, NULL},
    {"logmeoff", wts_logmeoff, METH_NOARGS, NULL},
    {"shutdown", wts_shutdown, METH_NOARGS, NULL},
    {NULL, NULL} /* sentinel */
};

static int
add_wts_constants(PyObject *module)
{
    PyObject *state2name;
    PyObject *state_value, *state_name;
    int status;

    state2name = PyDict_New();
    if (state2name == NULL)
        return -1;

#define ADD_ENUM_CONSTANT(e) do { \
        if (PyModule_AddIntConstant(module, #e, e) < 0) \
            return -1; \
    } while (0) /* omit ';' */

#define ADD_ENUM_TO_STATE2NAME(e) do { \
        state_value = PyInt_FromLong(e); \
        state_name = PyString_FromString(#e); \
        status = PyDict_SetItem(state2name, state_value, state_name); \
        Py_XDECREF(state_value); \
        Py_XDECREF(state_name); \
        if (status < 0) { \
            Py_DECREF(state2name); \
            return -1; \
        } \
    } while (0) /* omit ';' */

#define WTS_STATE_CONSTANTS(F) \
    F(WTSActive); \
    F(WTSConnected); \
    F(WTSConnectQuery); \
    F(WTSShadow); \
    F(WTSDisconnected); \
    F(WTSIdle); \
    F(WTSListen); \
    F(WTSReset); \
    F(WTSDown); \
    F(WTSInit) /* omit ';' */

    WTS_STATE_CONSTANTS(ADD_ENUM_CONSTANT);
    WTS_STATE_CONSTANTS(ADD_ENUM_TO_STATE2NAME);

#undef ADD_ENUM_TO_STATE2NAME
#undef ADD_ENUM_CONSTANT
#undef WTS_STATE_CONSTANTS

    if (PyModule_AddObject(module, "state2name", state2name) < 0)
        return -1;

    return 0;
}

PyMODINIT_FUNC
initwts(void)
{
    PyObject *module;
    
    module = Py_InitModule3("wts", wts_methods, wts_doc);
    if (module == NULL)
        return;
    if (!initialized) {
        PyStructSequence_InitType(&StructSessionInfoType,
                                  &struct_session_info_desc);
        initialized = 1;
    }
    Py_INCREF(&StructSessionInfoType);
    if (PyModule_AddObject(module, "SessionInfo", 
                          (PyObject *)&StructSessionInfoType) < 0)
        return;
    add_wts_constants(module);
}
