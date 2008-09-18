#!/usr/bin/env python

from distutils.core import setup, Extension

wtsmodule = Extension("wts", ["wtsmodule.c"], libraries=["wtsapi32"])

setup(name="wts",
      author="Alexandre Vassalotti",
      author_email="alexandre@peadrop.com",
      description="Simple Windows Terminal Service API interface",
      version="0.2",
      license="GNU GPL v2",
      ext_modules=[wtsmodule])

