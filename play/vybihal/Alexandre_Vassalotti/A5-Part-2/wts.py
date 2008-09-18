"""Simple Python interface to the Windows Terminal Service API.
"""

import win32ts
import socket
import os
import operator

__author__ = "Alexandre Vassalotti <alexandre@peadrop.com>"
__all__ = ["listusers", "logoff", "logmeoff", "shutdown"]
__version__ = "0.1"
__license__ = "GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.txt>"

def _add_enum_constants(enum_constants):
    global state2name
    state2name = {}
    module_dict = globals()
    for i, name in enumerate(enum_constants):
        module_dict[name] = i
        state2name[i] = name

_enum_constants = (
    'WTSActive',
    'WTSConnected',
    'WTSConnectQuery',
    'WTSShadow',
    'WTSDisconnected',
    'WTSIdle',
    'WTSListen',
    'WTSReset',
    'WTSDown',
    'WTSInit'
)

_add_enum_constants(_enum_constants)
del _add_enum_constants
del _enum_constants

class WTSServer:

    def __init__(self, hostname):
        self.hostname = hostname
        self.handle = win32ts.WTSOpenServer(hostname)

    def close(self):
        win32ts.WTSCloseServer(self.handle)

    def __del__(self):
        self.close()


class SessionInfo(tuple):
    """SessionInfo(session_id, state, username)"""

    __slots__ = ()

    def __new__(cls, session_id, state, username):
        return tuple.__new__(cls, (session_id, state, username))

    def __repr__(self):
        return "SessionInfo(session_id=%s, state=%s, username=%s)" % self

    session_id = property(operator.itemgetter(0))
    state = property(operator.itemgetter(1))
    username = property(operator.itemgetter(2))


def listusers():
    server = WTSServer(socket.gethostname())
    results = []
    for session in win32ts.WTSEnumerateSessions(server.handle):
        session_id = session['SessionId']
        state = session['State']
        username = win32ts.WTSQuerySessionInformation(
            server.handle, session_id, win32ts.WTSUserName)
        results.append(SessionInfo(session_id, state, username))
    return results

def logoff(session_id):
    if session_id < 0:
        raise ValueError("session ID must be non-negative")
    server = WTSServer(socket.gethostname())
    win32ts.WTSLogoffSession(server.handle, session_id, True)

def logmeoff():
    server = WTSServer(socket.gethostname())
    session_id = win32ts.ProcessIdToSessionId(os.getpid())
    return logoff(session_id)

def shutdown():
    server = WTSServer(socket.gethostname())
    win32ts.ShutdownSystem(server.handle, win32ts.WTS_WSD_POWEROFF)

