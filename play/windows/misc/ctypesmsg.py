import os, sys, ctypes
#too bad this isn't asynchronous... maybe we could find an async version
# so that our script keeps on going... or run it as a thread?
ctypes.windll.user32.MessageBoxA(0,
    "curdir: %s\nexedir: %s\nsys.winver: %s" % (
        os.path.abspath(os.curdir),
        os.path.abspath(os.path.dirname(sys.argv[0])),
        sys.winver,
    ), "%s - Message" % os.path.basename(sys.executable), 0x30
)